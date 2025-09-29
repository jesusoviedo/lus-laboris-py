"""
RAG service for question answering using LLM with context from Qdrant
"""
import os
import time
import textwrap
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

# LLM imports
from openai import OpenAI
import google.genai as genai
from google.genai import types

# Retry imports
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings
from .embedding_service import embedding_service
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
        
        logger.info(f"RAG service initialized with provider: {self.llm_provider}, model: {self.llm_model}")
    
    def _initialize_llm_clients(self):
        """Initialize LLM clients based on provider"""
        try:
            if self.llm_provider == "openai":
                # Configure OpenAI with API key from settings
                openai_api_key = settings.openai_api_key
                if openai_api_key:
                    self.openai_client = OpenAI(api_key=openai_api_key)
                else:
                    self.openai_client = OpenAI()  # Will use OPENAI_API_KEY env var as fallback
                logger.info("OpenAI client initialized")
            elif self.llm_provider == "gemini":
                # Configure Gemini with API key from settings
                gemini_api_key = settings.gemini_api_key
                if gemini_api_key:
                    self.genai_client.configure(api_key=gemini_api_key)
                else:
                    self.genai_client.configure() # Will use GEMINI_API_KEY env var as fallback
                logger.info("Gemini client initialized")
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
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
                return {"status": "unhealthy", "error": f"Collection {self.collection_name} does not exist"}
            
            # Check reranking service
            reranking_status = reranking_service.health_check()
            
            return {
                "status": "healthy",
                "provider": self.llm_provider,
                "model": self.llm_model,
                "collection_name": self.collection_name,
                "top_k": self.top_k,
                "embedding_model": self.embedding_model,
                "reranking": reranking_status
            }
        except Exception as e:
            logger.error(f"RAG service health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def _retrieve_documents(self, query: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Retrieve relevant documents from Qdrant with optional reranking"""
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_single_embedding(
                query, 
                model_name=self.embedding_model
            )
            
            # Search in Qdrant - get more documents if reranking is enabled
            search_limit = self.top_k * 2 if settings.api_use_reranking else self.top_k
            search_results = qdrant_service.search_documents(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=search_limit
            )
            
            # Apply reranking if enabled
            if settings.api_use_reranking and search_results:
                reranked_docs, rerank_metadata = reranking_service.rerank_documents(
                    query=query,
                    documents=search_results,
                    top_k=self.top_k
                )
                return reranked_docs, rerank_metadata
            else:
                return search_results, {"reranking_applied": False}
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Build context from retrieved documents"""
        if not documents:
            return "No se encontraron documentos relevantes."
        
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            # Extract information from document
            payload = doc['payload']
            articulo_text = payload.get('articulo', 'Texto no disponible')
            capitulo_descripcion = payload.get('capitulo_descripcion', 'Descripción no disponible')
            articulo_numero = payload.get('articulo_numero', 'N/A')
            
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=60))
    def _generate_openai_response(self, prompt: str) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado en derecho laboral paraguayo."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=2, max=60))
    def _generate_gemini_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        try:
            model = self.gemini_client.GenerativeModel(
                model_name=self.llm_model,
                system_instruction="Eres un asistente especializado en derecho laboral paraguayo."
            )
            
            response = model.generate_content(
                prompt,
                generation_config=types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1500
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _generate_response(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate response using LLM with context from documents"""
        if not documents:
            return "No se encontraron documentos relevantes para responder la pregunta."
        
        # Build context
        context_text = self._build_context(documents)
        
        # Create prompt
        prompt = self._create_prompt(query, context_text)
        
        # Generate response
        if self.llm_provider == "openai":
            response = self._generate_openai_response(prompt)
        elif self.llm_provider == "gemini":
            response = self._generate_gemini_response(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        return response
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a question using RAG pipeline"""
        start_time = time.time()
        
        try:
            # Retrieve relevant documents with optional reranking
            documents, retrieval_metadata = self._retrieve_documents(question)
            
            # Generate response
            answer = self._generate_response(question, documents)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare response
            response = {
                "success": True,
                "question": question,
                "answer": answer,
                "processing_time_seconds": round(processing_time, 3),
                "documents_retrieved": len(documents),
                "top_k": self.top_k,
                "reranking_applied": retrieval_metadata.get("reranking_applied", False),
                "documents": [
                    {
                        "id": doc["id"],
                        "score": round(doc["score"], 4),
                        "rerank_score": round(doc.get("rerank_score", 0), 4) if doc.get("rerank_score") else None,
                        "payload": {
                            "articulo_numero": doc["payload"].get("articulo_numero"),
                            "capitulo_descripcion": doc["payload"].get("capitulo_descripcion"),
                            "articulo": doc["payload"].get("articulo", "")[:200] + "..." if len(doc["payload"].get("articulo", "")) > 200 else doc["payload"].get("articulo", "")
                        }
                    }
                    for doc in documents
                ]
            }
            
            logger.info(f"Question answered successfully in {processing_time:.3f}s")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to answer question: {str(e)}")
            
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "processing_time_seconds": round(processing_time, 3)
            }


# Global service instance
rag_service = RAGService()
