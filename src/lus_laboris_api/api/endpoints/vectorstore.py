"""
Vectorstore endpoints for Qdrant operations
"""
import os
import json
import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from pathlib import Path

from ..models.requests import LoadToVectorstoreRequest, LoadToVectorstoreLocalRequest, LoadToVectorstoreGCPRequest
from ..models.responses import LoadToVectorstoreResponse, CollectionInfoResponse, CollectionsListResponse, CollectionDeleteResponse
from ..services.qdrant_service import qdrant_service
from ..services.gcp_service import gcp_service
from ..services.embedding_service import embedding_service
from ..auth.security import require_vectorstore_write, get_current_user
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["vectorstore"])


@router.post(
    "/load-to-vectorstore",
    response_model=LoadToVectorstoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Load data to vectorstore",
    description="Load JSON data from local files or GCS into Qdrant vector database"
)
async def load_to_vectorstore(
    request: LoadToVectorstoreRequest,
    current_user: str = Depends(require_vectorstore_write)
):
    """Load data to vectorstore from local files or GCS"""
    try:
        start_time = time.time()
        
        # Load data based on mode
        if request.mode == "local":
            data = await _load_local_data(request)
        elif request.mode == "gcp":
            data = await _load_gcp_data(request)
        else:
            raise ValueError(f"Unsupported mode: {request.mode}")
        
        # Process data and generate embeddings
        documents, embeddings, embedding_metadata = await _process_data_for_embedding(
            data, settings.api_default_embedding_model, settings.api_embedding_batch_size
        )
        
        # Use configured collection name
        collection_name = settings.api_qdrant_collection_name
        
        # Create collection in Qdrant
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
            batch_size=request.batch_size
        )
        
        processing_time = time.time() - start_time
        
        return LoadToVectorstoreResponse(
            success=True,
            message="Data loaded successfully to vectorstore",
            collection_name=collection_name,
            documents_processed=documents_processed,
            documents_inserted=documents_inserted,
            processing_time_seconds=processing_time,
            embedding_model_used=embedding_metadata["model_name"],
            vector_dimensions=vector_size,
            batch_size=request.batch_size
        )
        
    except Exception as e:
        logger.error(f"Failed to load data to vectorstore: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data to vectorstore: {str(e)}"
        )


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
    collection_name: str,
    current_user: str = Depends(require_vectorstore_write)
):
    """Delete a collection"""
    try:
        success = qdrant_service.delete_collection(collection_name)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found"
            )
        
        return CollectionDeleteResponse(
            success=True,
            message=f"Collection '{collection_name}' deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete collection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete collection: {str(e)}"
        )


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
    status_code=status.HTTP_201_CREATED,
    summary="Load data to vectorstore from local files",
    description="Load JSON data from local files into Qdrant vector database"
)
async def load_to_vectorstore_local(
    request: LoadToVectorstoreLocalRequest,
    current_user: str = Depends(require_vectorstore_write)
):
    """Load data to vectorstore from local files"""
    try:
        start_time = time.time()
        
        # Load data from local file
        data = await _load_local_data_new(request)
        
        # Process data and generate embeddings
        documents, embeddings, embedding_metadata = await _process_data_for_embedding(
            data, settings.api_default_embedding_model, settings.api_embedding_batch_size
        )
        
        # Use configured collection name
        collection_name = settings.api_qdrant_collection_name
        
        # Create collection in Qdrant
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
            batch_size=request.batch_size
        )
        
        processing_time = time.time() - start_time
        
        return LoadToVectorstoreResponse(
            success=True,
            message="Data loaded successfully to vectorstore from local files",
            collection_name=collection_name,
            documents_processed=documents_processed,
            documents_inserted=documents_inserted,
            processing_time_seconds=processing_time,
            embedding_model_used=embedding_metadata["model_name"],
            vector_dimensions=vector_size,
            batch_size=request.batch_size
        )
        
    except Exception as e:
        logger.error(f"Failed to load data to vectorstore from local files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data to vectorstore from local files: {str(e)}"
        )


@router.post(
    "/load-to-vectorstore-gcp",
    response_model=LoadToVectorstoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Load data to vectorstore from GCS",
    description="Load JSON data from Google Cloud Storage into Qdrant vector database"
)
async def load_to_vectorstore_gcp(
    request: LoadToVectorstoreGCPRequest,
    current_user: str = Depends(require_vectorstore_write)
):
    """Load data to vectorstore from GCS"""
    try:
        start_time = time.time()
        
        # Load data from GCS
        data = await _load_gcp_data_new(request)
        
        # Process data and generate embeddings
        documents, embeddings, embedding_metadata = await _process_data_for_embedding(
            data, settings.api_default_embedding_model, settings.api_embedding_batch_size
        )
        
        # Use configured collection name
        collection_name = settings.api_qdrant_collection_name
        
        # Create collection in Qdrant
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
            batch_size=request.batch_size
        )
        
        processing_time = time.time() - start_time
        
        return LoadToVectorstoreResponse(
            success=True,
            message="Data loaded successfully to vectorstore from GCS",
            collection_name=collection_name,
            documents_processed=documents_processed,
            documents_inserted=documents_inserted,
            processing_time_seconds=processing_time,
            embedding_model_used=embedding_metadata["model_name"],
            vector_dimensions=vector_size,
            batch_size=request.batch_size
        )
        
    except Exception as e:
        logger.error(f"Failed to load data to vectorstore from GCS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load data to vectorstore from GCS: {str(e)}"
        )


async def _load_local_data(request: LoadToVectorstoreRequest) -> Dict[str, Any]:
    """Load data from local JSON file"""
    try:
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent.parent
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


async def _load_gcp_data(request: LoadToVectorstoreRequest) -> Dict[str, Any]:
    """Load data from GCS"""
    try:
        if not request.bucket_name:
            raise ValueError("Bucket name is required for GCP mode")
        
        # Construct file path in GCS
        file_path = f"processed/{request.filename}"
        
        logger.info(f"Loading GCP data from: gs://{request.bucket_name}/{file_path}")
        
        data = gcp_service.load_json_from_gcs(
            bucket_name=request.bucket_name,
            file_path=file_path,
            credentials_path=request.gcp_credentials_path
        )
        
        logger.info(f"Loaded {len(data.get('articulos', []))} articles from GCS")
        return data
        
    except Exception as e:
        logger.error(f"Failed to load GCP data: {str(e)}")
        raise


async def _process_data_for_embedding(
    data: Dict[str, Any], 
    model_name: str, 
    batch_size: int
) -> tuple:
    """Process data and generate embeddings"""
    try:
        # Extract articles
        articles = data.get('articulos', [])
        if not articles:
            raise ValueError("No articles found in data")
        
        # Prepare documents for embedding
        documents = []
        texts = []
        
        for article in articles:
            # Create document payload
            doc = {
                "text": article.get('articulo', ''),
                "article_number": article.get('articulo_numero'),
                "libro": article.get('libro'),
                "titulo": article.get('titulo'),
                "capitulo": article.get('capitulo'),
                "capitulo_descripcion": article.get('capitulo_descripcion'),
                "source": "labor_law_paraguay"
            }
            
            # Create text for embedding (chapter + article)
            chapter = article.get('capitulo_descripcion', '')
            article_text = article.get('articulo', '')
            text_for_embedding = f"{chapter}: {article_text}"
            
            documents.append(doc)
            texts.append(text_for_embedding)
        
        logger.info(f"Processing {len(documents)} documents for embedding")
        
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


def _generate_collection_name(request: LoadToVectorstoreRequest) -> str:
    """Generate collection name based on request parameters"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    mode = request.mode
    filename = Path(request.filename).stem
    
    return f"labor_law_{mode}_{filename}_{timestamp}"


async def _load_local_data_new(request: LoadToVectorstoreLocalRequest) -> Dict[str, Any]:
    """Load data from local JSON file (new endpoint)"""
    try:
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent.parent
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


def _generate_collection_name_local(request: LoadToVectorstoreLocalRequest) -> str:
    """Generate collection name for local endpoint"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(request.filename).stem
    
    return f"labor_law_local_{filename}_{timestamp}"


def _generate_collection_name_gcp(request: LoadToVectorstoreGCPRequest) -> str:
    """Generate collection name for GCP endpoint"""
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(request.filename).stem
    bucket = request.bucket_name.replace("-", "_")
    
    return f"labor_law_gcp_{bucket}_{filename}_{timestamp}"
