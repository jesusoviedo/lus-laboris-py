"""
Qdrant service for vector database operations
"""
import os
import time
import logging
import warnings
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter
from qdrant_client.http import models as rest
import numpy as np
from ..config import settings

logger = logging.getLogger(__name__)

# Suppress Qdrant API key warning for local development (HTTP + API key)
warnings.filterwarnings("ignore", message="Api key is used with an insecure connection")


class QdrantService:
    """Service for Qdrant vector database operations"""
    
    def __init__(self):
        self.client = None
        self.qdrant_url = settings.api_qdrant_url
        self.qdrant_api_key = settings.api_qdrant_api_key
        self.prefer_grpc = settings.api_qdrant_prefer_grpc
        self.grpc_port = settings.api_qdrant_grpc_port
        self._connect()
    
    def _connect(self):
        """Connect to Qdrant with optimized settings (gRPC preferred)"""
        try:
            # Parse URL to check if it's local or remote
            is_local = "localhost" in self.qdrant_url or "127.0.0.1" in self.qdrant_url
            
            # Configuración optimizada
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                timeout=10.0,              # Timeout explícito (10 segundos)
                prefer_grpc=self.prefer_grpc,  # Use gRPC cuando esté disponible (2-3x más rápido)
                grpc_port=self.grpc_port,  # Puerto gRPC (default: 6334)
                https=not is_local,        # HTTPS solo para conexiones remotas
            )
            
            # Log connection type (check for gRPC methods)
            has_grpc = hasattr(self.client, 'grpc_points') or hasattr(self.client, 'grpc_collections')
            connection_type = "gRPC" if has_grpc and self.prefer_grpc else "HTTP"
            logger.info(f"Connected to Qdrant at {self.qdrant_url} using {connection_type}")
            
            if connection_type == "gRPC":
                logger.info(f"gRPC port: {self.grpc_port} - Performance optimized (2-3x faster than HTTP)")
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant with gRPC: {str(e)}")
            logger.warning("Falling back to HTTP connection...")
            
            # Fallback: intentar sin gRPC
            try:
                self.client = QdrantClient(
                    url=self.qdrant_url,
                    api_key=self.qdrant_api_key,
                    timeout=10.0,
                    prefer_grpc=False,  # Forzar HTTP
                )
                logger.info(f"Connected to Qdrant at {self.qdrant_url} using HTTP (fallback)")
                logger.warning("gRPC not available - using HTTP (slower). Check Qdrant gRPC port configuration.")
            except Exception as e2:
                logger.error(f"Failed to connect to Qdrant even with HTTP: {str(e2)}")
                raise ConnectionError(f"Failed to connect to Qdrant: {str(e2)}")
    
    def health_check(self) -> Dict[str, str]:
        """Check Qdrant health status"""
        try:
            # Try to get collections info
            collections = self.client.get_collections()
            
            # Detect connection type (check for gRPC methods)
            has_grpc = hasattr(self.client, 'grpc_points') or hasattr(self.client, 'grpc_collections')
            connection_type = "gRPC" if has_grpc else "HTTP"
            
            return {
                "status": "connected",
                "collections_count": len(collections.collections),
                "connection_type": connection_type
            }
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return {"status": "disconnected", "error": str(e)}
    
    def create_collection(
        self, 
        collection_name: str, 
        vector_size: int, 
        distance: Distance = Distance.COSINE,
        replace_existing: bool = False
    ) -> bool:
        """Create a new collection in Qdrant"""
        try:
            # Check if collection exists
            if self.collection_exists(collection_name):
                if replace_existing:
                    logger.info(f"Deleting existing collection: {collection_name}")
                    self.client.delete_collection(collection_name)
                else:
                    logger.warning(f"Collection {collection_name} already exists")
                    return False
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            
            logger.info(f"Collection '{collection_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {str(e)}")
            raise
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.get_collections()
            return any(col.name == collection_name for col in collections.collections)
        except Exception as e:
            logger.error(f"Failed to check collection existence: {str(e)}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection information"""
        try:
            if not self.collection_exists(collection_name):
                return None
            
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "status": collection_info.status.value
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            return None
    
    def insert_documents(
        self,
        collection_name: str,
        documents: List[Dict[str, Any]],
        embeddings: np.ndarray,
        batch_size: int = 100
    ) -> Tuple[int, int]:
        """Insert documents with embeddings into collection"""
        try:
            if not self.collection_exists(collection_name):
                raise ValueError(f"Collection {collection_name} does not exist")
            
            total_documents = len(documents)
            inserted_count = 0
            
            # Process in batches
            for i in range(0, total_documents, batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_embeddings = embeddings[i:i + batch_size]
                
                # Prepare points
                points = []
                for j, (doc, embedding) in enumerate(zip(batch_docs, batch_embeddings)):
                    point = PointStruct(
                        id=i + j,
                        vector=embedding.tolist(),
                        payload=doc
                    )
                    points.append(point)
                
                # Insert batch
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                inserted_count += len(points)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(points)} documents")
            
            logger.info(f"Successfully inserted {inserted_count}/{total_documents} documents")
            return total_documents, inserted_count
            
        except Exception as e:
            logger.error(f"Failed to insert documents: {str(e)}")
            raise
    
    def search_documents(
        self,
        collection_name: str,
        query_vector: np.ndarray,
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Filter] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if not self.collection_exists(collection_name):
                raise ValueError(f"Collection {collection_name} does not exist")
            
            # Prepare search parameters
            search_params = {
                "collection_name": collection_name,
                "query": query_vector.tolist(),
                "limit": limit,
                "with_payload": True,
                "with_vectors": True
            }
            
            if score_threshold is not None:
                search_params["score_threshold"] = score_threshold
            
            if filter_conditions is not None:
                search_params["query_filter"] = filter_conditions
            
            # Perform search
            results = self.client.query_points(**search_params)
            
            # Format results
            formatted_results = []
            for result in results.points:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {str(e)}")
            raise
    
    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection"""
        try:
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection {collection_name} does not exist")
                return False
            
            self.client.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {str(e)}")
            raise
    
    def get_collection_stats(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get collection statistics"""
        try:
            if not self.collection_exists(collection_name):
                return None
            
            collection_info = self.client.get_collection(collection_name)
            return {
                "points_count": collection_info.points_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "vector_size": collection_info.config.params.vectors.size,
                "distance_metric": collection_info.config.params.vectors.distance.value,
                "status": collection_info.status.value
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return None
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            return []


# Global service instance
qdrant_service = QdrantService()
