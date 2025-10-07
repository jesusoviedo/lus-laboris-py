"""
RAG endpoint for question answering
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ..models.requests import QuestionRequest
from ..models.responses import QuestionResponse
from ..services.rag_service import rag_service
from ..services.phoenix_service import phoenix_service
from ..services.evaluation_service import evaluation_service
from ..auth.security import get_current_user
from ..config import settings

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
                "The system will search for relevant legal documents and generate an answer using an LLM."
)
@limiter.limit(f"{settings.api_rate_limit_requests}/{settings.api_rate_limit_window}")
async def ask_question(
    request: Request,  # Required for rate limiting
    question_data: QuestionRequest
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
        
        # Crear sesión de monitoreo
        session_id = phoenix_service.create_session()
        
        # Answer the question using RAG service
        result = rag_service.answer_question(question_data.question, session_id)
        
        # Create response
        response = QuestionResponse(
            success=result["success"],
            message="Question answered successfully" if result["success"] else "Failed to answer question",
            question=result["question"],
            answer=result.get("answer"),
            error=result.get("error"),
            processing_time_seconds=result["processing_time_seconds"],
            documents_retrieved=result.get("documents_retrieved"),
            top_k=result.get("top_k"),
            reranking_applied=result.get("reranking_applied"),
            documents=result.get("documents"),
            session_id=result.get("session_id")
        )
        
        if result["success"]:
            logger.info(f"Question answered successfully in {result['processing_time_seconds']:.3f}s for session {session_id}")
        else:
            logger.error(f"Failed to answer question: {result.get('error')}")
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error in ask_question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Finalizar sesión si se creó
        if session_id:
            phoenix_service.end_session(session_id)


@router.get(
    "/health",
    summary="RAG service health check",
    description="Check the health status of the RAG service and its dependencies"
)
async def rag_health_check() -> Dict[str, Any]:
    """Check RAG service health status"""
    try:
        health_status = rag_service.health_check()
        
        if health_status["status"] == "healthy":
            return {
                "success": True,
                "message": "RAG service is healthy",
                "timestamp": datetime.now().isoformat(),
                "status": health_status
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "success": False,
                    "message": "RAG service is unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "status": health_status
                }
            )
            
    except Exception as e:
        logger.error(f"RAG health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "RAG health check failed",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


@router.get(
    "/metrics",
    summary="Get Phoenix monitoring metrics",
    description="Get current Phoenix monitoring metrics and session statistics"
)
async def get_phoenix_metrics(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get Phoenix monitoring metrics"""
    try:
        # Obtener métricas del servicio Phoenix
        active_sessions = len(phoenix_service.session_tracker)
        
        # Calcular métricas agregadas
        total_actions = 0
        total_llm_calls = 0
        
        for session_data in phoenix_service.session_tracker.values():
            total_actions += len(session_data.get("actions", []))
            total_llm_calls += len(session_data.get("llm_calls", []))
        
        return {
            "success": True,
            "message": "Phoenix metrics retrieved successfully",
            "timestamp": datetime.now().isoformat(),
            "phoenix_enabled": phoenix_service.enabled,
            "active_sessions": active_sessions,
            "total_actions": total_actions,
            "total_llm_calls": total_llm_calls,
            "project_name": phoenix_service.project_name
        }
        
    except Exception as e:
        logger.error(f"Failed to get Phoenix metrics: {str(e)}")
        return {
            "success": False,
            "message": "Failed to get Phoenix metrics",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get(
    "/evaluations/status",
    summary="Get evaluation service status",
    description="Get current status of the asynchronous evaluation service"
)
async def get_evaluation_status(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get evaluation service status"""
    try:
        health = evaluation_service.health_check()
        
        return {
            "success": True,
            "message": "Evaluation service status retrieved successfully",
            "timestamp": datetime.now().isoformat(),
            "evaluation_service": health
        }
        
    except Exception as e:
        logger.error(f"Failed to get evaluation status: {str(e)}")
        return {
            "success": False,
            "message": "Failed to get evaluation status",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
