"""
Embedding service for generating vector embeddings
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from ..config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using various models"""
    
    def __init__(self):
        self.models = {}
        self.default_model = settings.api_embedding_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Embedding service initialized on device: {self.device}")
    
    def health_check(self) -> Dict[str, str]:
        """Check embedding service health status"""
        try:
            # Try to load default model if not already loaded
            if self.default_model not in self.models:
                self._load_model(self.default_model)
            
            model_info = self.models[self.default_model]
            return {
                "status": "healthy",
                "default_model": self.default_model,
                "device": self.device,
                "loaded_models": list(self.models.keys()),
                "model_dimensions": model_info["dimensions"]
            }
        except Exception as e:
            logger.error(f"Embedding service health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}
    
    def _load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a specific embedding model"""
        try:
            if model_name in self.models:
                logger.info(f"Model {model_name} already loaded")
                return self.models[model_name]
            
            logger.info(f"Loading embedding model: {model_name}")
            start_time = time.time()
            
            # Load model
            model = SentenceTransformer(model_name, device=self.device)
            
            # Get model info
            model_info = {
                "model": model,
                "name": model_name,
                "dimensions": model.get_sentence_embedding_dimension(),
                "device": self.device,
                "load_time": time.time() - start_time
            }
            
            # Cache model
            self.models[model_name] = model_info
            
            logger.info(f"Model {model_name} loaded successfully in {model_info['load_time']:.2f}s")
            return model_info
            
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")
            raise
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        if model_name not in self.models:
            try:
                self._load_model(model_name)
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {str(e)}")
                return None
        
        return self.models[model_name]
    
    def generate_embeddings(
        self,
        texts: List[str],
        model_name: Optional[str] = None,
        batch_size: int = 32,
        normalize_embeddings: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Generate embeddings for a list of texts"""
        try:
            # Use default model if not specified
            if model_name is None:
                model_name = self.default_model
            
            # Load model if not already loaded
            model_info = self.get_model_info(model_name)
            if not model_info:
                raise ValueError(f"Failed to load model: {model_name}")
            
            model = model_info["model"]
            
            logger.info(f"Generating embeddings for {len(texts)} texts using {model_name}")
            start_time = time.time()
            
            # Generate embeddings
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=normalize_embeddings,
                show_progress_bar=True
            )
            
            processing_time = time.time() - start_time
            
            # Prepare metadata
            metadata = {
                "model_name": model_name,
                "texts_count": len(texts),
                "embedding_dimensions": embeddings.shape[1],
                "processing_time_seconds": processing_time,
                "batch_size": batch_size,
                "normalize_embeddings": normalize_embeddings,
                "device": self.device
            }
            
            logger.info(f"Generated embeddings in {processing_time:.2f}s")
            return embeddings, metadata
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise
    
    def generate_single_embedding(
        self,
        text: str,
        model_name: Optional[str] = None
    ) -> np.ndarray:
        """Generate embedding for a single text"""
        try:
            embeddings, _ = self.generate_embeddings([text], model_name)
            return embeddings[0]
        except Exception as e:
            logger.error(f"Failed to generate single embedding: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """Get list of available/preloaded models"""
        return list(self.models.keys())
    
    def preload_model(self, model_name: str) -> bool:
        """Preload a model for faster subsequent use"""
        try:
            self._load_model(model_name)
            return True
        except Exception as e:
            logger.error(f"Failed to preload model {model_name}: {str(e)}")
            return False
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory"""
        try:
            if model_name in self.models:
                del self.models[model_name]
                logger.info(f"Model {model_name} unloaded")
                return True
            else:
                logger.warning(f"Model {model_name} not loaded")
                return False
        except Exception as e:
            logger.error(f"Failed to unload model {model_name}: {str(e)}")
            return False
    
    def get_model_dimensions(self, model_name: str) -> Optional[int]:
        """Get the dimension size of a specific model"""
        model_info = self.get_model_info(model_name)
        return model_info["dimensions"] if model_info else None
    
    def calculate_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
        metric: str = "cosine"
    ) -> float:
        """Calculate similarity between two embeddings"""
        try:
            if metric == "cosine":
                # Cosine similarity
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                return dot_product / (norm1 * norm2)
            elif metric == "dot":
                # Dot product
                return np.dot(embedding1, embedding2)
            elif metric == "euclidean":
                # Euclidean distance (inverted for similarity)
                distance = np.linalg.norm(embedding1 - embedding2)
                return 1 / (1 + distance)
            else:
                raise ValueError(f"Unsupported similarity metric: {metric}")
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {str(e)}")
            raise


# Global service instance
embedding_service = EmbeddingService()
