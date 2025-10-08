"""
FastAPI main application for Lus Laboris API
"""
import os
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .endpoints import vectorstore, health, rag
from .auth.jwt_handler import jwt_validator
from .auth.security import optional_auth
from .services.qdrant_service import qdrant_service
from .services.gcp_service import gcp_service
from .services.embedding_service import embedding_service
from .services.rag_service import rag_service
from .services.evaluation_service import evaluation_service
from .utils.cache import health_check_cache
from .config import settings
from .models.responses import RootResponse, ServiceStatusResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _sanitize_service_status(status: Dict[str, Any], is_authenticated: bool) -> Dict[str, Any]:
    """
    Sanitizar información sensible de servicios según autenticación.
    Reutiliza la misma lógica que los health checks individuales.
    """
    if is_authenticated:
        # Usuario autenticado: retornar información completa
        return status
    
    # Usuario no autenticado: retornar solo información básica
    sanitized = {
        "status": status.get("status", "unknown")
    }
    
    # Solo incluir información no sensible
    if "error" in status and not is_authenticated:
        sanitized["error"] = "Service unavailable"  # No exponer detalles del error
    
    return sanitized


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Lus Laboris API...")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        
        # Check Qdrant connection
        qdrant_status = qdrant_service.health_check()
        if qdrant_status.get("status") != "connected":
            logger.warning(f"Qdrant connection issue: {qdrant_status}")
        
        # Check GCP connection
        gcp_status = gcp_service.health_check()
        if gcp_status.get("status") != "connected":
            logger.warning(f"GCP connection issue: {gcp_status}")
        
        # Initialize embedding service
        embedding_status = embedding_service.health_check()
        if embedding_status.get("status") != "healthy":
            logger.warning(f"Embedding service issue: {embedding_status}")
        
        # Initialize RAG service
        rag_status = rag_service.health_check()
        if rag_status.get("status") != "healthy":
            logger.warning(f"RAG service issue: {rag_status}")
        
        # Initialize evaluation service
        eval_status = evaluation_service.health_check()
        logger.info(f"Evaluation service status: {eval_status.get('status')}")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Lus Laboris API...")
    
    # Shutdown evaluation service gracefully
    try:
        evaluation_service.shutdown()
        logger.info("Evaluation service shut down successfully")
    except Exception as e:
        logger.error(f"Error shutting down evaluation service: {e}")


# Create FastAPI application
app = FastAPI(
    title="Lus Laboris API",
    description="API for semantic search and retrieval of Paraguayan labor law information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.api_allowed_hosts
)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Include routers
app.include_router(health.router)
app.include_router(vectorstore.router)
app.include_router(rag.router)


# Root endpoint
@app.get(
    "/",
    response_model=RootResponse,
    summary="API Root",
    description="Get basic API information"
)
async def root():
    """Root endpoint with API information"""
    return RootResponse(
        success=True,
        message="Lus Laboris API is running",
        version="1.0.0",
        docs_url="/docs",
        health_check="/api/health"
    )






# Service status endpoint (Public with Info Filtering)
@app.get(
    "/api/status",
    response_model=ServiceStatusResponse,
    summary="Service Status",
    description="Get status of all services (optional authentication for detailed info)"
)
async def get_service_status(
    token_payload: Dict[str, Any] = Depends(optional_auth)
):
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
                "rag_service": sanitized_rag
            }
        )
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service status"
        )


if __name__ == "__main__":
    host = settings.api_host
    port = settings.api_port
    reload = settings.api_reload
    log_level = settings.api_log_level
    
    logger.info(f"Starting API server on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    logger.info(f"Log level: {log_level}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )
