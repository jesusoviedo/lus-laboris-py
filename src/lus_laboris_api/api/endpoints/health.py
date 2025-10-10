"""
Health check endpoints
"""
import time
import asyncio
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
from ..services.phoenix_service import phoenix_service
from ..auth.security import optional_auth
from ..utils.cache import health_check_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["Health"])

# Store startup time for uptime calculation
startup_time = time.time()


def _sanitize_health_response(status: Dict[str, Any], is_authenticated: bool) -> Dict[str, Any]:
    """
    Sanitize sensitive information in health checks based on authentication.
    Without authentication: only basic status
    With authentication: full information
    """
    if is_authenticated:
        # Authenticated user: return full information
        return status
    
    # Unauthenticated user: return only basic status (no additional fields)
    sanitized = {
        "status": status.get("status", "unknown")
    }
    
    # Don't include error, message, or any other fields without authentication
    # This ensures consistent response: only {"status": "..."}
    
    return sanitized


@router.get(
    "/",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check the health status of the API and its dependencies"
)
async def health_check():
    """Comprehensive health check endpoint with parallel execution"""
    try:
        # Calculate uptime
        uptime_seconds = time.time() - startup_time
        
        # Check service dependencies in parallel (OPTIMIZED)
        # Execute all health checks simultaneously
        health_check_tasks = await asyncio.gather(
            asyncio.to_thread(qdrant_service.health_check),
            asyncio.to_thread(gcp_service.health_check),
            asyncio.to_thread(embedding_service.health_check),
            asyncio.to_thread(reranking_service.health_check),
            asyncio.to_thread(rag_service.health_check),
            asyncio.to_thread(evaluation_service.health_check),
            asyncio.to_thread(phoenix_service.health_check),
            return_exceptions=True  # Don't fail if one fails
        )
        
        # Extract results
        qdrant_status = health_check_tasks[0] if not isinstance(health_check_tasks[0], Exception) else {"status": "error"}
        gcp_status = health_check_tasks[1] if not isinstance(health_check_tasks[1], Exception) else {"status": "error"}
        embedding_status = health_check_tasks[2] if not isinstance(health_check_tasks[2], Exception) else {"status": "error"}
        reranking_status = health_check_tasks[3] if not isinstance(health_check_tasks[3], Exception) else {"status": "error"}
        rag_status = health_check_tasks[4] if not isinstance(health_check_tasks[4], Exception) else {"status": "error"}
        eval_status = health_check_tasks[5] if not isinstance(health_check_tasks[5], Exception) else {"status": "error"}
        phoenix_status = health_check_tasks[6] if not isinstance(health_check_tasks[6], Exception) else {"status": "error"}
        
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
            "evaluation_service": eval_status.get("status", "unknown"),
            "phoenix": phoenix_status.get("status", "unknown")
        }
        
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
    """Check Qdrant service health with caching"""
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("qdrant")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            status = qdrant_service.health_check()
            # Save to cache
            health_check_cache.set("qdrant", status)
        
        # Sanitizar información sensible si no está autenticado
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") == "connected",
            "message": "Qdrant is healthy" if status.get("status") == "connected" else "Qdrant has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        return {
            "success": False,
            "message": "Qdrant health check failed",
            "status": {"status": "error"},
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
    """Check GCP service health with caching"""
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("gcp")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            status = gcp_service.health_check()
            # Save to cache
            health_check_cache.set("gcp", status)
        
        # Sanitizar información sensible si no está autenticado
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") == "connected",
            "message": "GCP is healthy" if status.get("status") == "connected" else "GCP has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"GCP health check failed: {str(e)}")
        return {
            "success": False,
            "message": "GCP health check failed",
            "status": {"status": "error"},
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
    """Check embedding service health with caching"""
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("embedding")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            status = embedding_service.health_check()
            # Save to cache
            health_check_cache.set("embedding", status)
        
        # Sanitizar información sensible si no está autenticado
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") == "healthy",
            "message": "Embedding service is healthy" if status.get("status") == "healthy" else "Embedding service has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Embedding service health check failed: {str(e)}")
        return {
            "success": False,
            "message": "Embedding service health check failed",
            "status": {"status": "error"},
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
    """Check reranking service health with caching"""
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("reranking")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            status = reranking_service.health_check()
            # Save to cache
            health_check_cache.set("reranking", status)
        
        # Sanitizar información sensible si no está autenticado
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") == "healthy",
            "message": "Reranking service is healthy" if status.get("status") == "healthy" else "Reranking service has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Reranking service health check failed: {str(e)}")
        return {
            "success": False,
            "message": "Reranking service health check failed",
            "status": {"status": "error"},
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
    """Check RAG service health with caching"""
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("rag")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            status = rag_service.health_check()
            # Save to cache
            health_check_cache.set("rag", status)
        
        # Sanitizar información sensible si no está autenticado
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") == "healthy",
            "message": "RAG service is healthy" if status.get("status") == "healthy" else "RAG service has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"RAG service health check failed: {str(e)}")
        return {
            "success": False,
            "message": "RAG service health check failed",
            "status": {"status": "error"},
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


@router.get(
    "/phoenix",
    response_model=Dict[str, Any],
    summary="Phoenix monitoring health check",
    description="Check Phoenix monitoring service status and connection"
)
async def phoenix_health_check(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
    """
    Check Phoenix monitoring service health with caching
    
    **Optional authentication** with smart information filtering:
    - **Without token**: Returns only basic status (healthy/disabled/unhealthy)
    - **With JWT token**: Returns detailed info + performs connection test to Phoenix collector
    """
    try:
        is_authenticated = token_payload is not None
        
        # Try to get from cache first
        cached_status = health_check_cache.get("phoenix")
        if cached_status is not None:
            status = cached_status
        else:
            # Not in cache, execute health check
            if is_authenticated:
                # Extended health check with connection test (only for authenticated users)
                status = phoenix_service.health_check_extended()
            else:
                # Basic health check (for public access)
                status = phoenix_service.health_check()
            
            # Save to cache
            health_check_cache.set("phoenix", status)
        
        # Sanitize sensitive information if not authenticated
        sanitized_status = _sanitize_health_response(status, is_authenticated)
        
        return {
            "success": status.get("status") in ["healthy", "disabled"],
            "message": "Phoenix monitoring is healthy" if status.get("status") == "healthy" else "Phoenix monitoring has issues",
            "status": sanitized_status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Phoenix health check failed: {str(e)}")
        return {
            "success": False,
            "message": "Phoenix health check failed",
            "status": {"status": "error"},
            "timestamp": time.time()
        }
