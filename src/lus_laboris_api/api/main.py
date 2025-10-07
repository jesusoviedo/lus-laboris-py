"""
FastAPI main application for Lus Laboris API
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .endpoints import vectorstore, health, rag
from .auth.jwt_handler import jwt_validator
from .services.qdrant_service import qdrant_service
from .services.gcp_service import gcp_service
from .services.embedding_service import embedding_service
from .services.rag_service import rag_service
from .services.evaluation_service import evaluation_service
from .config import settings
from .models.responses import RootResponse, ServiceStatusResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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






# Service status endpoint
@app.get(
    "/api/status",
    response_model=ServiceStatusResponse,
    summary="Service Status",
    description="Get detailed status of all services"
)
async def get_service_status():
    """Get detailed status of all services"""
    try:
        qdrant_status = qdrant_service.health_check()
        gcp_status = gcp_service.health_check()
        embedding_status = embedding_service.health_check()
        rag_status = rag_service.health_check()
        
        return ServiceStatusResponse(
            success=True,
            message="Service status retrieved successfully",
            services={
                "qdrant": qdrant_status,
                "gcp": gcp_status,
                "embedding_service": embedding_status,
                "rag_service": rag_status
            }
        )
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service status: {str(e)}"
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
