"""
Pydantic models for API responses
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseResponse):
    """Error response model"""
    error_code: Optional[str] = Field(None, description="Error code for debugging")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class LoadToVectorstoreResponse(BaseResponse):
    """Response model for loading data to vectorstore"""
    collection_name: str = Field(..., description="Name of the created/updated collection")
    documents_processed: int = Field(..., description="Number of documents processed")
    documents_inserted: int = Field(..., description="Number of documents successfully inserted")
    processing_time_seconds: float = Field(..., description="Total processing time in seconds")
    embedding_model_used: str = Field(..., description="Embedding model used for processing")
    vector_dimensions: int = Field(..., description="Dimension of the generated vectors")
    batch_size: int = Field(..., description="Batch size used for processing")
    job_id: Optional[str] = Field(None, description="Unique job identifier for background processing")
    job_status_url: Optional[str] = Field(None, description="URL to check job status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data loaded successfully to vectorstore",
                "timestamp": "2024-01-15T10:30:00Z",
                "collection_name": "labor_law_articles",
                "documents_processed": 410,
                "documents_inserted": 410,
                "processing_time_seconds": 45.2,
                "embedding_model_used": "sentence-transformers/all-MiniLM-L6-v2",
                "vector_dimensions": 384,
                "batch_size": 100
            }
        }


class HealthCheckResponse(BaseResponse):
    """Response model for health check"""
    service: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")
    dependencies: Dict[str, str] = Field(..., description="Status of service dependencies")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Service is healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "service": "lus-laboris-api",
                "version": "1.0.0",
                "status": "healthy",
                "dependencies": {
                    "qdrant": "connected",
                    "gcp": "connected",
                    "embedding_model": "loaded"
                },
                "uptime_seconds": 3600.5
            }
        }




class CollectionInfoResponse(BaseResponse):
    """Response model for collection information"""
    collection_name: str = Field(..., description="Name of the collection")
    points_count: int = Field(..., description="Number of points in the collection")
    vector_size: int = Field(..., description="Size of vectors in the collection")
    distance_metric: str = Field(..., description="Distance metric used")
    indexed_vectors_count: int = Field(..., description="Number of indexed vectors")
    payload_schema: Optional[Dict[str, Any]] = Field(None, description="Payload schema if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Collection information retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "collection_name": "labor_law_articles",
                "points_count": 410,
                "vector_size": 384,
                "distance_metric": "Cosine",
                "indexed_vectors_count": 410,
                "payload_schema": {
                    "text": "string",
                    "article_number": "integer",
                    "chapter": "string"
                }
            }
        }


class RootResponse(BaseResponse):
    """Response model for root endpoint"""
    version: str = Field(..., description="API version")
    docs_url: str = Field(..., description="URL to API documentation")
    health_check: str = Field(..., description="URL to health check endpoint")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Lus Laboris API is running",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "docs_url": "/docs",
                "health_check": "/api/health"
            }
        }


class ServiceStatusResponse(BaseResponse):
    """Response model for service status endpoint"""
    services: Dict[str, Any] = Field(..., description="Status of all services")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Service status retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "qdrant": {"status": "connected", "collections_count": 5},
                    "gcp": {"status": "connected", "buckets_count": 2},
                    "embedding_service": {"status": "healthy", "loaded_models": ["all-MiniLM-L6-v2"]}
                }
            }
        }


class CollectionsListResponse(BaseResponse):
    """Response model for collections list endpoint"""
    collections: List[str] = Field(..., description="List of collection names")
    count: int = Field(..., description="Number of collections")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Collections retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "collections": ["labor_law_articles", "test_collection"],
                "count": 2
            }
        }


class CollectionDeleteResponse(BaseResponse):
    """Response model for collection deletion"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Collection 'labor_law_articles' deleted successfully",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class JobStatusResponse(BaseResponse):
    """Response model for background job status"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: queued, processing, completed, failed")
    operation: str = Field(..., description="Operation type")
    user: str = Field(..., description="User who initiated the job")
    created_at: float = Field(..., description="Job creation timestamp")
    started_at: Optional[float] = Field(None, description="Job start timestamp")
    completed_at: Optional[float] = Field(None, description="Job completion timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    session_id: Optional[str] = Field(None, description="Phoenix monitoring session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Job status retrieved successfully",
                "timestamp": "2024-01-15T10:30:00Z",
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "operation": "load_to_vectorstore_local",
                "user": "admin",
                "created_at": 1705315800.0,
                "started_at": 1705315801.0,
                "completed_at": 1705315845.0,
                "result": {
                    "documents_processed": 410,
                    "documents_inserted": 410,
                    "processing_time_seconds": 44.0
                },
                "session_id": "660e8400-e29b-41d4-a716-446655440001"
            }
        }


class QuestionResponse(BaseResponse):
    """Response model for RAG question answering"""
    question: str = Field(..., description="The original question")
    answer: Optional[str] = Field(None, description="The generated answer (required when success=True)")
    error: Optional[str] = Field(None, description="Error message (only present when success=False)")
    processing_time_seconds: float = Field(..., description="Processing time in seconds")
    session_id: Optional[str] = Field(None, description="Phoenix monitoring session ID")
    # Source transparency fields (required when success=True)
    documents_retrieved: Optional[int] = Field(None, description="Number of documents retrieved from the knowledge base (required when success=True)")
    top_k: Optional[int] = Field(None, description="Number of most relevant documents considered (required when success=True)")
    reranking_applied: Optional[bool] = Field(None, description="Whether reranking was applied to improve document relevance (required when success=True)")
    documents: Optional[List[Dict[str, Any]]] = Field(None, description="Source documents used to generate the answer (required when success=True)")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "message": "Question answered successfully",
                    "timestamp": "2024-01-15T10:30:00Z",
                    "question": "¿Cuáles son los derechos del trabajador en caso de despido?",
                    "answer": "Según el Código del Trabajo paraguayo, el trabajador tiene derecho a...",
                    "processing_time_seconds": 2.345,
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "documents_retrieved": 5,
                    "top_k": 5,
                    "reranking_applied": True,
                    "documents": [
                        {
                            "id": 123,
                            "score": 0.8542,
                            "payload": {
                                "articulo_numero": 45,
                                "capitulo_descripcion": "Derechos del Trabajador",
                                "articulo": "El trabajador tiene derecho a..."
                            }
                        }
                    ]
                }
            ]
        }
