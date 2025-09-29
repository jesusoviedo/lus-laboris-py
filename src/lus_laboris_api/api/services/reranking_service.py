"""
Reranking service for improving document relevance using cross-encoders
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import CrossEncoder
from ..config import settings

logger = logging.getLogger(__name__)


class RerankingService:
    """Service for reranking documents using cross-encoder models"""
    
    def __init__(self):
        self.model_name = settings.api_reranking_model
        self.use_reranking = settings.api_use_reranking
        self.model = None
        
        if self.use_reranking and self.model_name:
            self._load_model()
            logger.info(f"Reranking service initialized with model: {self.model_name}")
        else:
            logger.info("Reranking service initialized but disabled")
    
    def _load_model(self):
        """Load the reranking model"""
        try:
            self.model = CrossEncoder(self.model_name)
            logger.info(f"Reranking model '{self.model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load reranking model '{self.model_name}': {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check reranking service health status"""
        try:
            if not self.use_reranking:
                return {
                    "status": "disabled",
                    "message": "Reranking is disabled in configuration"
                }
            
            if not self.model_name:
                return {
                    "status": "unhealthy",
                    "error": "No reranking model configured"
                }
            
            if not self.model:
                return {
                    "status": "unhealthy",
                    "error": "Reranking model not loaded"
                }
            
            return {
                "status": "healthy",
                "model_name": self.model_name,
                "use_reranking": self.use_reranking
            }
        except Exception as e:
            logger.error(f"Reranking service health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def rerank_documents(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Rerank documents based on query relevance using cross-encoder
        
        Args:
            query: The search query
            documents: List of documents to rerank
            top_k: Number of top documents to return (if None, returns all)
            
        Returns:
            Tuple of (reranked_documents, metadata)
        """
        if not self.use_reranking or not self.model:
            logger.debug("Reranking disabled or model not loaded, returning original documents")
            return documents, {"reranking_applied": False}
        
        if not documents:
            return documents, {"reranking_applied": False}
        
        try:
            logger.info(f"Reranking {len(documents)} documents with model: {self.model_name}")
            
            # Prepare query-document pairs for reranking
            query_doc_pairs = []
            for doc in documents:
                # Extract text content for reranking
                payload = doc.get('payload', {})
                articulo_text = payload.get('articulo', '')
                capitulo_descripcion_text = payload.get('capitulo_descripcion', '')
                doc_text = f"{capitulo_descripcion_text}: {articulo_text}"
                query_doc_pairs.append([query, doc_text])
            
            # Get reranking scores
            rerank_scores = self.model.predict(query_doc_pairs)
            
            # Add rerank scores to documents and sort by score
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(rerank_scores[i])
            
            # Sort by rerank score (descending)
            reranked_documents = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            
            # Apply top_k if specified
            if top_k is not None:
                reranked_documents = reranked_documents[:top_k]
            
            metadata = {
                "reranking_applied": True,
                "model_name": self.model_name,
                "documents_reranked": len(documents),
                "documents_returned": len(reranked_documents),
                "rerank_scores_range": {
                    "min": float(np.min(rerank_scores)),
                    "max": float(np.max(rerank_scores)),
                    "mean": float(np.mean(rerank_scores))
                }
            }
            
            logger.info(f"Reranking completed: {len(reranked_documents)} documents returned")
            return reranked_documents, metadata
            
        except Exception as e:
            logger.error(f"Failed to rerank documents: {str(e)}")
            # Return original documents if reranking fails
            return documents, {
                "reranking_applied": False,
                "error": str(e)
            }


# Global service instance
reranking_service = RerankingService()
