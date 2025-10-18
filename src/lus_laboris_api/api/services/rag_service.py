"""
RAG service for question answering using LLM with context from Qdrant
"""

import logging
import textwrap
import time
from typing import Any

from google import genai
from google.genai import types

# LLM imports
from openai import AsyncOpenAI  # Async client for better performance

# Retry imports
from tenacity import AsyncRetrying, retry, stop_after_attempt, wait_exponential

from ..config import settings
from .embedding_service import embedding_service
from .evaluation_service import evaluation_service
from .phoenix_service import phoenix_service
from .qdrant_service import qdrant_service
from .reranking_service import reranking_service

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based question answering"""

    def __init__(self):
        self.llm_provider = settings.api_llm_provider.lower()
        self.llm_model = settings.api_llm_model
        self.collection_name = settings.api_qdrant_collection_name
        self.top_k = settings.api_rag_top_k
        self.embedding_model = settings.api_embedding_model

        # Initialize LLM clients
        self._initialize_llm_clients()

        logger.info(
            f"RAG service initialized with provider: {self.llm_provider}, model: {self.llm_model}"
        )

    def _initialize_llm_clients(self):
        """Initialize LLM clients based on provider (async-ready)"""
        try:
            if self.llm_provider == "openai":
                # Configure OpenAI with async client for better performance
                openai_api_key = settings.openai_api_key
                if openai_api_key:
                    self.openai_client = AsyncOpenAI(api_key=openai_api_key)
                else:
                    self.openai_client = (
                        AsyncOpenAI()
                    )  # Will use OPENAI_API_KEY env var as fallback
                logger.info("OpenAI async client initialized (non-blocking)")
            elif self.llm_provider == "gemini":
                # Configure Gemini module with API key
                gemini_api_key = settings.gemini_api_key
                if gemini_api_key:
                    genai.configure(api_key=gemini_api_key)
                else:
                    genai.configure()  # Will use GEMINI_API_KEY env var as fallback
                logger.info("Gemini configured successfully")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        except Exception as e:
            logger.exception("Failed to initialize LLM client")
            raise

    def health_check(self) -> dict[str, Any]:
        """Check RAG service health status"""
        try:
            # Check embedding service
            embedding_status = embedding_service.health_check()
            if embedding_status.get("status") != "healthy":
                return {"status": "unhealthy", "error": "Embedding service not healthy"}

            # Check Qdrant service
            qdrant_status = qdrant_service.health_check()
            if qdrant_status.get("status") != "connected":
                return {"status": "unhealthy", "error": "Qdrant service not connected"}

            # Check collection exists
            if not qdrant_service.collection_exists(self.collection_name):
                return {
                    "status": "unhealthy",
                    "error": f"Collection {self.collection_name} does not exist",
                }

            # Check reranking service
            reranking_status = reranking_service.health_check()

            return {
                "status": "healthy",
                "provider": self.llm_provider,
                "model": self.llm_model,
                "embedding_model": self.embedding_model,
                "reranking": reranking_status,
            }
        except Exception as e:
            logger.exception("RAG service health check failed")
            return {"status": "unhealthy", "error": str(e)}

    def _retrieve_documents(
        self, query: str, session_id: str
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Retrieve relevant documents from Qdrant with optional reranking"""
        try:
            # Generate query embedding
            embedding_start = time.time()
            query_embedding = embedding_service.generate_single_embedding(
                query, model_name=self.embedding_model
            )
            embedding_time = time.time() - embedding_start

            # Track embedding generation
            phoenix_service.track_embedding_generation(
                session_id=session_id,
                text=query,
                model=self.embedding_model,
                generation_time=embedding_time,
            )

            # Search in Qdrant - get more documents if reranking is enabled
            search_start = time.time()
            search_limit = self.top_k * 2 if settings.api_use_reranking else self.top_k
            search_results = qdrant_service.search_documents(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=search_limit,
            )
            search_time = time.time() - search_start

            # Track vectorstore search
            phoenix_service.track_vectorstore_search(
                session_id=session_id,
                query=query,
                results_count=len(search_results),
                search_time=search_time,
            )

            # Apply reranking if enabled
            if settings.api_use_reranking and search_results:
                rerank_start = time.time()
                reranked_docs, rerank_metadata = reranking_service.rerank_documents(
                    query=query, documents=search_results, top_k=self.top_k
                )
                rerank_time = time.time() - rerank_start

                # Track reranking
                phoenix_service.track_reranking(
                    session_id=session_id,
                    query=query,
                    documents_count=len(search_results),
                    reranking_time=rerank_time,
                )

                return reranked_docs, rerank_metadata
            return search_results, {"reranking_applied": False}

        except Exception as e:
            logger.exception("Failed to retrieve documents")
            raise

    def _build_context(self, documents: list[dict[str, Any]]) -> str:
        """Build context from retrieved documents"""
        if not documents:
            return "No se encontraron documentos relevantes."

        context_parts = []

        for i, doc in enumerate(documents, 1):
            # Extract information from document
            payload = doc["payload"]
            articulo_text = payload.get("articulo", "Texto no disponible")
            capitulo_descripcion = payload.get("capitulo_descripcion", "Descripción no disponible")
            articulo_numero = payload.get("articulo_numero", "N/A")

            # Format document
            doc_text = f"{articulo_text} [Capítulo: {capitulo_descripcion} - Artículo número: {articulo_numero}]"
            context_parts.append(f"Documento {i}:\n{doc_text}\n")

        return "\n".join(context_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """Create prompt for LLM"""
        prompt = textwrap.dedent(f"""\
            Eres un asistente especializado en derecho laboral paraguayo.
            Responde la pregunta del usuario basándote únicamente en el contexto proporcionado.

            CONTEXTO:
            {context}

            PREGUNTA: {query}

            INSTRUCCIONES:
            - Responde de manera clara y precisa
            - Basa tu respuesta únicamente en el contexto proporcionado
            - Si el contexto no contiene información suficiente, indícalo claramente
            - Cita los artículos específicos cuando sea relevante
            - Mantén un tono profesional y técnico apropiado para el ámbito legal

            RESPUESTA:""")

        return prompt

    async def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI (async for better performance)"""
        try:
            # Use AsyncRetrying for async retry logic
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=60)
            ):
                with attempt:
                    response = await self.openai_client.chat.completions.create(
                        model=self.llm_model,
                        messages=[
                            {
                                "role": "system",
                                "content": "Eres un asistente especializado en derecho laboral paraguayo.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                        max_tokens=1500,
                    )

                    return response.choices[0].message.content.strip()

        except Exception as e:
            logger.exception("OpenAI API error")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=60))
    def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            # Create model instance for this request
            # Note: This is lightweight - just creates a Python object, not a network connection
            model = genai.GenerativeModel(
                model_name=self.llm_model,
                system_instruction="Eres un asistente especializado en derecho laboral paraguayo.",
            )

            response = model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(temperature=0.2, max_output_tokens=1500),
            )

            return response.text.strip()

        except Exception as e:
            logger.exception("Gemini API error")
            raise

    async def _generate_response(
        self, query: str, documents: list[dict[str, Any]], session_id: str
    ) -> str:
        """Generate response using LLM with context from documents (async)"""
        if not documents:
            return "No relevant documents found to answer the question."

        # Build context
        context_text = self._build_context(documents)

        # Create prompt
        prompt = self._create_prompt(query, context_text)

        # Generate response (async)
        if self.llm_provider == "openai":
            response = await self._generate_openai_response(prompt)
        elif self.llm_provider == "gemini":
            response = self._generate_gemini_response(prompt)  # Gemini still synchronous
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        # Track LLM call
        phoenix_service.track_llm_call(
            session_id=session_id,
            provider=self.llm_provider,
            model=self.llm_model,
            prompt=prompt,
            response=response,
            metadata={
                "context_length": len(context_text),
                "documents_count": len(documents),
                "query": query,
            },
        )

        return response

    async def answer_question(self, question: str, session_id: str | None = None) -> dict[str, Any]:
        """Answer a question using RAG pipeline with Phoenix monitoring (async)"""
        start_time = time.time()

        # Create session if not provided
        if not session_id:
            session_id = phoenix_service.create_session()

        try:
            # Retrieve relevant documents with optional reranking
            documents, retrieval_metadata = self._retrieve_documents(question, session_id)

            # Generate response (async)
            answer = await self._generate_response(question, documents, session_id)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Build full context for evaluation
            context_text = self._build_context(documents)

            # Enqueue asynchronous evaluation (non-blocking response)
            evaluation_service.enqueue_evaluation(
                session_id=session_id,
                question=question,
                context=context_text,
                answer=answer,
                documents=documents,
                metadata={
                    "processing_time": processing_time,
                    "llm_provider": self.llm_provider,
                    "llm_model": self.llm_model,
                    "reranking_applied": retrieval_metadata.get("reranking_applied", False),
                    "top_k": self.top_k,
                },
            )

            # Prepare response
            response = {
                "success": True,
                "question": question,
                "answer": answer,
                "processing_time_seconds": round(processing_time, 3),
                "documents_retrieved": len(documents),
                "top_k": self.top_k,
                "reranking_applied": retrieval_metadata.get("reranking_applied", False),
                "session_id": session_id,
                "documents": [
                    {
                        "id": doc["id"],
                        "score": round(doc["score"], 4),
                        "rerank_score": round(doc.get("rerank_score", 0), 4)
                        if doc.get("rerank_score")
                        else None,
                        "payload": {
                            "articulo_numero": doc["payload"].get("articulo_numero"),
                            "capitulo_descripcion": doc["payload"].get("capitulo_descripcion"),
                            "articulo": doc["payload"].get("articulo", "")[:200] + "..."
                            if len(doc["payload"].get("articulo", "")) > 200
                            else doc["payload"].get("articulo", ""),
                        },
                    }
                    for doc in documents
                ],
            }

            logger.info(
                f"Question answered successfully in {processing_time:.3f}s for session {session_id}"
            )
            logger.debug(f"Evaluation enqueued for asynchronous processing (session {session_id})")
            return response

        except Exception as e:
            processing_time = time.time() - start_time
            logger.exception("Failed to answer question")

            return {
                "success": False,
                "question": question,
                "error": str(e),
                "processing_time_seconds": round(processing_time, 3),
                "session_id": session_id,
            }


# Global service instance
rag_service = RAGService()
