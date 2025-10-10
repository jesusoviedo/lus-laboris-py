"""
Vectorstore endpoints for Qdrant operations
"""
import os
import json
import time
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from pathlib import Path

from ..models.requests import LoadToVectorstoreLocalRequest, LoadToVectorstoreGCPRequest
from ..models.responses import LoadToVectorstoreResponse, CollectionInfoResponse, CollectionsListResponse, CollectionDeleteResponse, JobStatusResponse
from ..services.qdrant_service import qdrant_service
from ..services.gcp_service import gcp_service
from ..services.embedding_service import embedding_service
from ..services.phoenix_service import phoenix_service
from ..auth.security import require_vectorstore_write, get_current_user
from ..auth.jwt_handler import jwt_validator
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["vectorstore"])

# Global dictionary to track background jobs
background_jobs: Dict[str, Dict[str, Any]] = {}


def _timestamp_to_datetime(timestamp: Optional[float]) -> Optional[str]:
    """Convert Unix timestamp to ISO 8601 datetime string"""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp).isoformat()


async def _load_to_vectorstore_background(
    job_id: str,
    request: LoadToVectorstoreLocalRequest,
    current_user: str,
    token_payload: Dict[str, Any]
):
    """Execute vectorstore loading in background"""
    session_id = None
    try:
        background_jobs[job_id]["status"] = "processing"
        background_jobs[job_id]["started_at"] = time.time()
        
        start_time = time.time()
        
        # Create Phoenix monitoring session
        session_id = phoenix_service.create_session(user_id=current_user)
        background_jobs[job_id]["session_id"] = session_id
        
        # Track operation start
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="load_to_vectorstore_local",
            collection_name=settings.api_qdrant_collection_name,
            metadata={
                "user": current_user,
                "token_payload": token_payload,
                "filename": request.filename,
                "local_data_path": request.local_data_path,
                "replace_collection": request.replace_collection,
                "job_id": job_id
            }
        )
        
        # Load data
        data = await _load_local_data_new(request)
        
        # Process and generate embeddings
        documents, embeddings, embedding_metadata = await _process_data_for_embedding(
            data, settings.api_embedding_model, settings.api_embedding_batch_size
        )
        
        # Create collection
        collection_name = settings.api_qdrant_collection_name
        vector_size = embeddings.shape[1]
        qdrant_service.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            replace_existing=request.replace_collection
        )
        
        # Insert documents
        documents_processed, documents_inserted = qdrant_service.insert_documents(
            collection_name=collection_name,
            documents=documents,
            embeddings=embeddings,
            batch_size=settings.api_embedding_batch_size
        )
        
        processing_time = time.time() - start_time
        
        # Track success
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="load_to_vectorstore_local_success",
            collection_name=collection_name,
            metadata={
                "documents_processed": documents_processed,
                "documents_inserted": documents_inserted,
                "processing_time_seconds": processing_time
            }
        )
        
        # Update job status
        background_jobs[job_id]["status"] = "completed"
        background_jobs[job_id]["completed_at"] = time.time()
        background_jobs[job_id]["result"] = {
            "documents_processed": documents_processed,
            "documents_inserted": documents_inserted,
            "processing_time_seconds": processing_time
        }
        
        logger.info(f"Background job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background job {job_id} failed: {str(e)}")
        
        # Track error
        if session_id:
            phoenix_service.track_vectorstore_operation(
                session_id=session_id,
                operation_type="load_to_vectorstore_local_error",
                collection_name=settings.api_qdrant_collection_name,
                metadata={"error": str(e)}
            )
        
        # Update job status
        background_jobs[job_id]["status"] = "failed"
        background_jobs[job_id]["completed_at"] = time.time()
        background_jobs[job_id]["error"] = str(e)
        
    finally:
        if session_id:
            phoenix_service.end_session(session_id)


async def _load_to_vectorstore_gcp_background(
    job_id: str,
    request: LoadToVectorstoreGCPRequest,
    current_user: str,
    token_payload: Dict[str, Any]
):
    """Execute GCP vectorstore loading in background"""
    session_id = None
    try:
        background_jobs[job_id]["status"] = "processing"
        background_jobs[job_id]["started_at"] = time.time()
        
        start_time = time.time()
        
        # Create Phoenix monitoring session
        session_id = phoenix_service.create_session(user_id=current_user)
        background_jobs[job_id]["session_id"] = session_id
        
        # Track operation start
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="load_to_vectorstore_gcp",
            collection_name=settings.api_qdrant_collection_name,
            metadata={
                "user": current_user,
                "token_payload": token_payload,
                "bucket_name": request.bucket_name,
                "filename": request.filename,
                "folder": request.folder,
                "replace_collection": request.replace_collection,
                "job_id": job_id
            }
        )
        
        # Load data from GCS
        data = await _load_gcp_data_new(request)
        
        # Process and generate embeddings
        documents, embeddings, embedding_metadata = await _process_data_for_embedding(
            data, settings.api_embedding_model, settings.api_embedding_batch_size
        )
        
        # Create collection
        collection_name = settings.api_qdrant_collection_name
        vector_size = embeddings.shape[1]
        qdrant_service.create_collection(
            collection_name=collection_name,
            vector_size=vector_size,
            replace_existing=request.replace_collection
        )
        
        # Insert documents
        documents_processed, documents_inserted = qdrant_service.insert_documents(
            collection_name=collection_name,
            documents=documents,
            embeddings=embeddings,
            batch_size=settings.api_embedding_batch_size
        )
        
        processing_time = time.time() - start_time
        
        # Track success
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="load_to_vectorstore_gcp_success",
            collection_name=collection_name,
            metadata={
                "documents_processed": documents_processed,
                "documents_inserted": documents_inserted,
                "processing_time_seconds": processing_time
            }
        )
        
        # Update job status
        background_jobs[job_id]["status"] = "completed"
        background_jobs[job_id]["completed_at"] = time.time()
        background_jobs[job_id]["result"] = {
            "documents_processed": documents_processed,
            "documents_inserted": documents_inserted,
            "processing_time_seconds": processing_time
        }
        
        logger.info(f"Background job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background job {job_id} failed: {str(e)}")
        
        # Track error
        if session_id:
            phoenix_service.track_vectorstore_operation(
                session_id=session_id,
                operation_type="load_to_vectorstore_gcp_error",
                collection_name=settings.api_qdrant_collection_name,
                metadata={"error": str(e)}
            )
        
        # Update job status
        background_jobs[job_id]["status"] = "failed"
        background_jobs[job_id]["completed_at"] = time.time()
        background_jobs[job_id]["error"] = str(e)
        
    finally:
        if session_id:
            phoenix_service.end_session(session_id)


def _extract_token_payload(request: Request) -> Dict[str, Any]:
    """Extract and decode JWT token payload from request"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # Decode token to get payload
            payload = jwt_validator.validate_token(token)
            return {
                "user": payload.get("sub", "unknown"),
                "email": payload.get("email", "unknown"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "token_exp": payload.get("exp"),
                "token_iat": payload.get("iat")
            }
    except Exception as e:
        logger.warning(f"Failed to extract token payload: {e}")
    
    return {"user": "unknown", "error": "token_not_decoded"}


@router.get(
    "/collections/{collection_name}",
    response_model=CollectionInfoResponse,
    summary="Get collection information",
    description="Get detailed information about a specific collection"
)
async def get_collection_info(
    collection_name: str,
    current_user: str = Depends(get_current_user)
):
    """Get collection information"""
    try:
        collection_info = qdrant_service.get_collection_info(collection_name)
        
        if not collection_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found"
            )
        
        return CollectionInfoResponse(
            success=True,
            message="Collection information retrieved successfully",
            collection_name=collection_info["name"],
            points_count=collection_info["points_count"],
            vector_size=collection_info["vector_size"],
            distance_metric=collection_info["distance_metric"],
            indexed_vectors_count=collection_info["indexed_vectors_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get collection info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection info: {str(e)}"
        )


@router.delete(
    "/collections/{collection_name}",
    response_model=CollectionDeleteResponse,
    summary="Delete collection",
    description="Delete a specific collection from Qdrant"
)
async def delete_collection(
    request: Request,
    collection_name: str,
    current_user: str = Depends(require_vectorstore_write)
):
    """Delete a collection"""
    session_id = None
    try:
        # Create sesión de monitoreo Phoenix
        session_id = phoenix_service.create_session(user_id=current_user)
        
        # Extract payload del token JWT
        token_payload = _extract_token_payload(request)
        
        # Track operación principal
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="delete_collection",
            collection_name=collection_name,
            metadata={
                "user": current_user,
                "token_payload": token_payload,
                "endpoint": "/api/data/collections/{collection_name}",
                "method": "DELETE"
            }
        )
        
        # Execute eliminación
        success = qdrant_service.delete_collection(collection_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found"
            )
        
        # Track resultado exitoso
        phoenix_service.track_vectorstore_operation(
            session_id=session_id,
            operation_type="delete_collection_success",
            collection_name=collection_name,
            metadata={
                "success": True,
                "collection_deleted": collection_name
            }
            )
        
        return CollectionDeleteResponse(
            success=True,
            message=f"Collection '{collection_name}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete collection: {str(e)}")
        
        # Track error
        if session_id:
            phoenix_service.track_vectorstore_operation(
                session_id=session_id,
                operation_type="delete_collection_error",
                collection_name=collection_name,
                metadata={"error": str(e)}
            )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete collection: {str(e)}"
        )
    finally:
        # Finalizar sesión Phoenix
        if session_id:
            phoenix_service.end_session(session_id)


@router.get(
    "/collections",
    response_model=CollectionsListResponse,
    summary="List collections",
    description="List all available collections in Qdrant"
)
async def list_collections(
    current_user: str = Depends(get_current_user)
):
    """List all collections"""
    try:
        collections = qdrant_service.list_collections()
        
        return CollectionsListResponse(
            success=True,
            message="Collections retrieved successfully",
            collections=collections,
            count=len(collections)
        )
        
    except Exception as e:
        logger.error(f"Failed to list collections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list collections: {str(e)}"
        )


@router.post(
    "/load-to-vectorstore-local",
    response_model=LoadToVectorstoreResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Load data to vectorstore from local files (async)",
    description="Initiates an asynchronous job to load JSON data from local files into Qdrant vector database"
)
async def load_to_vectorstore_local(
    http_request: Request,
    background_tasks: BackgroundTasks,
    request: LoadToVectorstoreLocalRequest,
    current_user: str = Depends(require_vectorstore_write)
):
    """Load data to vectorstore from local files (asynchronous processing)"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Extract JWT token payload
        token_payload = _extract_token_payload(http_request)
        
        # Initialize job status
        background_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "operation": "load_to_vectorstore_local",
            "user": current_user,
            "collection_name": settings.api_qdrant_collection_name,
            "filename": request.filename,
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None
        }
        
        # Add background task
        background_tasks.add_task(
            _load_to_vectorstore_background,
            job_id,
            request,
            current_user,
            token_payload
        )
        
        logger.info(f"Background job {job_id} queued for user {current_user}")
        
        # Return immediately with job information
        return LoadToVectorstoreResponse(
            success=True,
            message=f"Data loading job initiated successfully. Job ID: {job_id}. Check status at /api/data/jobs",
            collection_name=settings.api_qdrant_collection_name,
            documents_processed=0,  # Will be updated in background
            documents_inserted=0,   # Will be updated in background
            processing_time_seconds=0.0,
            embedding_model_used=settings.api_embedding_model,
            vector_dimensions=0,  # Will be determined in background
            batch_size=settings.api_embedding_batch_size,
            job_id=job_id
        )
        
    except Exception as e:
        logger.error(f"Failed to queue background job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate data loading job: {str(e)}"
        )


@router.post(
    "/load-to-vectorstore-gcp",
    response_model=LoadToVectorstoreResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Load data to vectorstore from GCS (async)",
    description="Initiates asynchronous loading of JSON data from Google Cloud Storage into Qdrant vector database"
)
async def load_to_vectorstore_gcp(
    http_request: Request,
    background_tasks: BackgroundTasks,
    request: LoadToVectorstoreGCPRequest,
    current_user: str = Depends(require_vectorstore_write)
):
    """Load data to vectorstore from GCS (asynchronous processing)"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Extract JWT token payload
        token_payload = _extract_token_payload(http_request)
        
        # Initialize job status
        background_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "operation": "load_to_vectorstore_gcp",
            "user": current_user,
            "collection_name": settings.api_qdrant_collection_name,
            "filename": request.filename,
            "bucket_name": request.bucket_name,
            "folder": request.folder,
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None
        }
        
        # Add background task
        background_tasks.add_task(
            _load_to_vectorstore_gcp_background,
            job_id,
            request,
            current_user,
            token_payload
        )
        
        logger.info(f"Background job {job_id} queued for user {current_user}")
        
        # Return immediately with job information
        return LoadToVectorstoreResponse(
            success=True,
            message=f"Data loading job initiated successfully. Job ID: {job_id}. Check status at /api/data/jobs",
            collection_name=settings.api_qdrant_collection_name,
            documents_processed=0,  # Will be updated in background
            documents_inserted=0,   # Will be updated in background
            processing_time_seconds=0.0,
            embedding_model_used=settings.api_embedding_model,
            vector_dimensions=0,  # Will be determined in background
            batch_size=settings.api_embedding_batch_size,
            job_id=job_id
        )
        
    except Exception as e:
        logger.error(f"Failed to queue background job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate data loading job: {str(e)}"
        )




async def _process_data_for_embedding(
    data: Dict[str, Any], 
    model_name: str, 
    batch_size: int
) -> tuple:
    """Process data and generate embeddings"""
    try:
        # Extract articles and metadata
        articles = data.get('articulos', [])
        meta = data.get('meta', {})
        
        if not articles:
            raise ValueError("No articles found in data")
        
        # Get law number for source generation
        numero_ley = meta.get('numero_ley', 'unknown')
        source = f"codigo_trabajo_paraguay_ley{numero_ley}"
        
        # Prepare documents for embedding
        documents = []
        texts = []
        
        for article in articles:
            # Extract fields
            capitulo_descripcion = article.get('capitulo_descripcion', '')
            articulo_text = article.get('articulo', '')
            articulo_len = len(articulo_text)
            
            # Create text for embedding (capitulo_descripcion: articulo)
            text_for_embedding = f"{capitulo_descripcion}: {articulo_text}"
            
            # Create document payload with all required fields
            doc = {
                "libro": article.get('libro'),
                "libro_numero": article.get('libro_numero'),
                "titulo": article.get('titulo'),
                "capitulo": article.get('capitulo'),
                "capitulo_numero": article.get('capitulo_numero'),
                "capitulo_descripcion": capitulo_descripcion,
                "articulo": articulo_text,
                "articulo_numero": article.get('articulo_numero'),
                "articulo_len": articulo_len,
                "source": source
            }
            
            documents.append(doc)
            texts.append(text_for_embedding)
        
        logger.info(f"Processing {len(documents)} documents for embedding")
        logger.info(f"Source: {source}")
        
        # Generate embeddings
        embeddings, embedding_metadata = embedding_service.generate_embeddings(
            texts=texts,
            model_name=model_name,
            batch_size=batch_size
        )
        
        return documents, embeddings, embedding_metadata
        
    except Exception as e:
        logger.error(f"Failed to process data for embedding: {str(e)}")
        raise




async def _load_local_data_new(request: LoadToVectorstoreLocalRequest) -> Dict[str, Any]:
    """Load data from local JSON file (new endpoint)"""
    try:
        # Get project root directory (go up from src/lus_laboris_api/api/endpoints/ to project root)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        data_path = project_root / (request.local_data_path or "data/processed")
        file_path = data_path / request.filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading local data from: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data.get('articulos', []))} articles from local file")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load local data: {str(e)}")
        raise


async def _load_gcp_data_new(request: LoadToVectorstoreGCPRequest) -> Dict[str, Any]:
    """Load data from GCS (new endpoint)"""
    try:
        if settings.api_gcp_use_credentials:
            # Use credentials file from config
            data = gcp_service.load_from_gcs_local(
                filename=request.filename,
                folder=request.folder,
                bucket_name=request.bucket_name,
                use_credentials=True,
                credentials_path=settings.api_google_application_credentials
            )
        else:
            # Use automatic credentials (cloud mode)
            data = gcp_service.load_from_gcs_cloud(
                filename=request.filename,
                folder=request.folder,
                bucket_name=request.bucket_name
            )
        
        logger.info(f"Loaded {len(data.get('articulos', []))} articles from GCS")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load GCP data: {str(e)}")
        raise


@router.get(
    "/jobs",
    status_code=status.HTTP_200_OK,
    summary="List all background jobs",
    description="Retrieve all background jobs (accessible by any authenticated user)"
)
async def list_all_jobs(
    current_user: str = Depends(require_vectorstore_write)
):
    """List all background jobs (accessible by any authenticated user)"""
    try:
        all_jobs = []
        
        for job_id, job_data in background_jobs.items():
            # Extract username if user is a dict (token payload)
            job_user = job_data["user"]
            if isinstance(job_user, dict):
                job_user = job_user.get("username") or job_user.get("sub")
            
            all_jobs.append({
                "job_id": job_data["job_id"],
                "status": job_data["status"],
                "operation": job_data["operation"],
                "user": job_user,
                "filename": job_data.get("filename"),
                "collection_name": job_data.get("collection_name"),
                "created_at": _timestamp_to_datetime(job_data["created_at"]),
                "started_at": _timestamp_to_datetime(job_data.get("started_at")),
                "completed_at": _timestamp_to_datetime(job_data.get("completed_at")),
                "error": job_data.get("error"),
                "result": job_data.get("result")
            })
        
        return {
            "success": True,
            "message": f"Found {len(all_jobs)} job(s)",
            "jobs": all_jobs,
            "count": len(all_jobs)
        }
        
    except Exception as e:
        logger.error(f"Failed to list all jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )

