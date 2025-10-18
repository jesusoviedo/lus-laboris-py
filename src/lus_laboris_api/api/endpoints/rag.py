"""
RAG endpoint for question answering
"""

import logging

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..models.requests import QuestionRequest
from ..models.responses import QuestionResponse
from ..services.phoenix_service import phoenix_service
from ..services.rag_service import rag_service

logger = logging.getLogger(__name__)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

# Create router
router = APIRouter(prefix="/api/rag", tags=["RAG"])


@router.post(
    "/ask",
    response_model=QuestionResponse,
    summary="Ask a question about Paraguayan labor law",
    description="Ask a question about Paraguayan labor law using RAG (Retrieval-Augmented Generation). "
    "The system will search for relevant legal documents and generate an answer using an LLM.",
)
@limiter.limit("{settings.api_rate_limit_requests}/{settings.api_rate_limit_window}")
async def ask_question(
    request: Request,  # Required for rate limiting
    question_data: QuestionRequest,
) -> QuestionResponse:
    """
    Ask a question about Paraguayan labor law using RAG

    This endpoint:
    1. Converts the question to an embedding
    2. Searches for relevant documents in Qdrant
    3. Generates an answer using an LLM (OpenAI or Gemini)
    4. Returns the answer with metadata

    Rate limit: {settings.api_rate_limit_requests} requests per {settings.api_rate_limit_window} per IP address
    """
    session_id = None
    try:
        logger.info(f"Received question: {question_data.question[:100]}...")

        # Create sesión de monitoreo
        session_id = phoenix_service.create_session()

        # Answer the question using RAG service (async)
        result = await rag_service.answer_question(question_data.question, session_id)

        # Create response
        response = QuestionResponse(
            success=result["success"],
            message="Question answered successfully"
            if result["success"]
            else "Failed to answer question",
            question=result["question"],
            answer=result.get("answer"),
            error=result.get("error"),
            processing_time_seconds=result["processing_time_seconds"],
            documents_retrieved=result.get("documents_retrieved"),
            top_k=result.get("top_k"),
            reranking_applied=result.get("reranking_applied"),
            documents=result.get("documents"),
            session_id=result.get("session_id"),
        )

        if result["success"]:
            logger.info(
                "Question answered successfully in {result['processing_time_seconds']:.3f}s for session {session_id}"
            )
        else:
            logger.error(f"Failed to answer question: {result.get('error')}")

        return response

    except Exception as e:
        logger.error(f"Unexpected error in ask_question: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e!s}",
        )
    finally:
        # Finalizar sesión si se creó
        if session_id:
            phoenix_service.end_session(session_id)
