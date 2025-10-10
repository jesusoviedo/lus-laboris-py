"""
FastAPI main application for Lus Laboris API
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .endpoints import health, rag, status, vectorstore
from .services.embedding_service import embedding_service
from .services.evaluation_service import evaluation_service
from .services.gcp_service import gcp_service
from .services.qdrant_service import qdrant_service
from .services.rag_service import rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
            logger.warning("Qdrant connection issue: {qdrant_status}")

        # Check GCP connection
        gcp_status = gcp_service.health_check()
        if gcp_status.get("status") != "connected":
            logger.warning("GCP connection issue: {gcp_status}")

        # Initialize embedding service
        embedding_status = embedding_service.health_check()
        if embedding_status.get("status") != "healthy":
            logger.warning("Embedding service issue: {embedding_status}")

        # Initialize RAG service
        rag_status = rag_service.health_check()
        if rag_status.get("status") != "healthy":
            logger.warning("RAG service issue: {rag_status}")

        # Initialize evaluation service
        eval_status = evaluation_service.health_check()
        logger.info("Evaluation service status: {eval_status.get('status')}")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.exception("Failed to initialize services")

    yield

    # Shutdown
    logger.info("Shutting down Lus Laboris API...")

    # Shutdown evaluation service gracefully
    try:
        evaluation_service.shutdown()
        logger.info("Evaluation service shut down successfully")
    except Exception as e:
        logger.exception("Error shutting down evaluation service")


# Create FastAPI application
app = FastAPI(
    title="Lus Laboris API",
    description="API for semantic search and retrieval of Paraguayan labor law information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
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
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.api_allowed_hosts)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "error_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error("Unhandled exception: {exc!s}")
    return JSONResponse(
        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        },
    )


# Include routers
app.include_router(status.router)  # Root and status endpoints
app.include_router(health.router)
app.include_router(vectorstore.router)
app.include_router(rag.router)


if __name__ == "__main__":
    host = settings.api_host
    port = settings.api_port
    reload = settings.api_reload
    log_level = settings.api_log_level

    logger.info("Starting API server on {host}:{port}")
    logger.info("Reload mode: {reload}")
    logger.info("Log level: {log_level}")

    uvicorn.run("main:app", host=host, port=port, reload=reload, log_level=log_level)
