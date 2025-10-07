"""
Health check endpoints
"""
import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends
from ..models.responses import HealthCheckResponse
from ..services.qdrant_service import qdrant_service
from ..services.gcp_service import gcp_service
from ..services.embedding_service import embedding_service
from ..services.reranking_service import reranking_service
from ..services.rag_service import rag_service
from ..services.evaluation_service import evaluation_service
from ..auth.security import optional_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])

# Store startup time for uptime calculation
startup_time = time.time()


@router.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Calculate uptime
        uptime_seconds = time.time() - startup_time
        
        # Check service dependencies
        qdrant_status = qdrant_service.health_check()
        gcp_status = gcp_service.health_check()
        embedding_status = embedding_service.health_check()
        reranking_status = reranking_service.health_check()
        rag_status = rag_service.health_check()
        eval_status = evaluation_service.health_check()
        
        # Determine overall health
        all_healthy = (
            qdrant_status.get("status") == "connected" and
            embedding_status.get("status") == "healthy" and
            rag_status.get("status") == "healthy"
        )
        
        # Prepare dependencies status
        dependencies = {
            "qdrant": qdrant_status.get("status", "unknown"),
            "embedding_service": embedding_status.get("status", "unknown"),
            "reranking_service": reranking_status.get("status", "unknown"),
            "rag_service": rag_status.get("status", "unknown"),
            "gcp": gcp_status.get("status", "unknown"),
            "evaluation_service": eval_status.get("status", "unknown")
        }
        
        # Add additional info if available
        if qdrant_status.get("collections_count") is not None:
            dependencies["qdrant_collections"] = str(qdrant_status["collections_count"])
        
        if gcp_status.get("buckets_count") is not None:
            dependencies["gcp_buckets"] = str(gcp_status["buckets_count"])
        
        if embedding_status.get("loaded_models"):
            dependencies["loaded_models"] = ", ".join(embedding_status["loaded_models"])
        
        if reranking_status.get("model_name"):
            dependencies["reranking_model"] = reranking_status["model_name"]
        
        if rag_status.get("provider"):
            dependencies["rag_provider"] = rag_status["provider"]
            dependencies["rag_model"] = rag_status.get("model", "unknown")
        
        if eval_status.get("queue_size") is not None:
            dependencies["evaluation_queue_size"] = str(eval_status["queue_size"])
            dependencies["phoenix_evals_available"] = str(eval_status.get("phoenix_evals_available", False))
        
        return HealthCheckResponse(
            success=all_healthy,
            message="Service is healthy" if all_healthy else "Service has issues",
            service="lus-laboris-api",
            version="1.0.0",
            status="healthy" if all_healthy else "degraded",
            dependencies=dependencies,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            success=False,
            message=f"Health check failed: {str(e)}",
            service="lus-laboris-api",
            version="1.0.0",
            status="unhealthy",
            dependencies={"error": str(e)},
            uptime_seconds=time.time() - startup_time
        )


@router.get(
    "/qdrant",
    response_model=Dict[str, Any],
    summary="Qdrant health check",
    description="Check Qdrant connection and status"
)
async def qdrant_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """Check Qdrant service health"""
    try:
        status = qdrant_service.health_check()
        
        return {
            "success": status.get("status") == "connected",
            "message": "Qdrant is healthy" if status.get("status") == "connected" else "Qdrant has issues",
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"Qdrant health check failed: {str(e)}",
            "status": {"status": "error", "error": str(e)},
            "timestamp": time.time()
        }


@router.get(
    "/gcp",
    response_model=Dict[str, Any],
    summary="GCP health check",
    description="Check Google Cloud Platform connection and status"
)
async def gcp_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """Check GCP service health"""
    try:
        status = gcp_service.health_check()
        
        return {
            "success": status.get("status") == "connected",
            "message": "GCP is healthy" if status.get("status") == "connected" else "GCP has issues",
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"GCP health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"GCP health check failed: {str(e)}",
            "status": {"status": "error", "error": str(e)},
            "timestamp": time.time()
        }


@router.get(
    "/embeddings",
    response_model=Dict[str, Any],
    summary="Embedding service health check",
    description="Check embedding service status and loaded models"
)
async def embedding_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """Check embedding service health"""
    try:
        status = embedding_service.health_check()
        
        return {
            "success": status.get("status") == "healthy",
            "message": "Embedding service is healthy" if status.get("status") == "healthy" else "Embedding service has issues",
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Embedding service health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"Embedding service health check failed: {str(e)}",
            "status": {"status": "error", "error": str(e)},
            "timestamp": time.time()
        }


@router.get(
    "/reranking",
    response_model=Dict[str, Any],
    summary="Reranking service health check",
    description="Check reranking service status and model"
)
async def reranking_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """Check reranking service health"""
    try:
        status = reranking_service.health_check()
        
        return {
            "success": status.get("status") == "healthy",
            "message": "Reranking service is healthy" if status.get("status") == "healthy" else "Reranking service has issues",
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Reranking service health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"Reranking service health check failed: {str(e)}",
            "status": {"status": "error", "error": str(e)},
            "timestamp": time.time()
        }


@router.get(
    "/rag",
    response_model=Dict[str, Any],
    summary="RAG service health check",
    description="Check RAG service status and configuration"
)
async def rag_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """Check RAG service health"""
    try:
        status = rag_service.health_check()
        
        return {
            "success": status.get("status") == "healthy",
            "message": "RAG service is healthy" if status.get("status") == "healthy" else "RAG service has issues",
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"RAG service health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"RAG service health check failed: {str(e)}",
            "status": {"status": "error", "error": str(e)},
            "timestamp": time.time()
        }


@router.get(
    "/ready",
    response_model=Dict[str, Any],
    summary="Readiness check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check():
    """Check if service is ready"""
    try:
        # Check critical dependencies
        qdrant_status = qdrant_service.health_check()
        embedding_status = embedding_service.health_check()
        rag_status = rag_service.health_check()
        
        ready = (
            qdrant_status.get("status") == "connected" and
            embedding_status.get("status") == "healthy" and
            rag_status.get("status") == "healthy"
        )
        
        return {
            "success": ready,
            "message": "Service is ready" if ready else "Service is not ready",
            "ready": ready,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "success": False,
            "message": f"Readiness check failed: {str(e)}",
            "ready": False,
            "timestamp": time.time()
        }
