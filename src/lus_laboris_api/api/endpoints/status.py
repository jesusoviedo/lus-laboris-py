"""
Status and root endpoints
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from ..auth.security import optional_auth
from ..models.responses import RootResponse, ServiceStatusResponse
from ..services.embedding_service import embedding_service
from ..services.gcp_service import gcp_service
from ..services.qdrant_service import qdrant_service
from ..services.rag_service import rag_service
from ..utils.cache import health_check_cache

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Status"])


def _sanitize_service_status(status: dict[str, Any], is_authenticated: bool) -> dict[str, Any]:
    """
    Sanitize sensitive service information based on authentication.
    Reuses the same logic as individual health checks.
    """
    if is_authenticated:
        # Authenticated user: return full information
        return status

    # Unauthenticated user: return only basic status (no additional fields)
    sanitized = {"status": status.get("status", "unknown")}

    # Don't include error, message, or any other fields without authentication
    # This ensures consistent response: only {"status": "..."}

    return sanitized


@router.get(
    "/", response_model=RootResponse, summary="API Root", description="Get basic API information"
)
async def root():
    """Root endpoint with API information"""
    return RootResponse(
        success=True,
        message="Lus Laboris API is running",
        version="1.0.0",
        docs_url="/docs",
        health_check="/api/health",
    )


@router.get(
    "/api/status",
    response_model=ServiceStatusResponse,
    summary="Service Status",
    description="Get status of all services (optional authentication for detailed info)",
)
async def get_service_status(token_payload: dict[str, Any] = Depends(optional_auth)):
    """
    Get status of all services

    **Optional authentication** with smart information filtering:
    - **Without token**: Returns only basic status (connected/healthy/unhealthy)
    - **With JWT token**: Returns detailed information (project IDs, models, counts, etc.)

    This allows public monitoring tools to check service health while protecting
    sensitive infrastructure details from unauthorized access.
    """
    try:
        is_authenticated = token_payload is not None

        # Get full status from all services (with cache)
        # Try cache first for each service
        qdrant_status = health_check_cache.get("qdrant") or qdrant_service.health_check()
        gcp_status = health_check_cache.get("gcp") or gcp_service.health_check()
        embedding_status = health_check_cache.get("embedding") or embedding_service.health_check()
        rag_status = health_check_cache.get("rag") or rag_service.health_check()

        # Update cache if it was a miss
        if health_check_cache.get("qdrant") is None:
            health_check_cache.set("qdrant", qdrant_status)
        if health_check_cache.get("gcp") is None:
            health_check_cache.set("gcp", gcp_status)
        if health_check_cache.get("embedding") is None:
            health_check_cache.set("embedding", embedding_status)
        if health_check_cache.get("rag") is None:
            health_check_cache.set("rag", rag_status)

        # Sanitize sensitive information based on authentication
        sanitized_qdrant = _sanitize_service_status(qdrant_status, is_authenticated)
        sanitized_gcp = _sanitize_service_status(gcp_status, is_authenticated)
        sanitized_embedding = _sanitize_service_status(embedding_status, is_authenticated)
        sanitized_rag = _sanitize_service_status(rag_status, is_authenticated)

        # Log access
        if is_authenticated:
            user = token_payload.get("sub", "unknown")
            logger.info(f"Detailed service status requested by authenticated user: {user}")
        else:
            logger.debug("Basic service status requested (no authentication)")

        return ServiceStatusResponse(
            success=True,
            message="Service status retrieved successfully",
            services={
                "qdrant": sanitized_qdrant,
                "gcp": sanitized_gcp,
                "embedding_service": sanitized_embedding,
                "rag_service": sanitized_rag,
            },
        )

    except Exception as e:
        logger.exception("Failed to get service status")
        return ServiceStatusResponse(
            success=False, message=f"Failed to retrieve service status: {e!s}", services={}
        )
