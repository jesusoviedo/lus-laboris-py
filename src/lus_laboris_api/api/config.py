"""
Configuration settings for the API
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    api_log_level: str = "info"
    
    # Security
    api_allowed_origins: List[str] = Field(default=["*"], json_schema_extra={"example": ["*"]})
    api_allowed_hosts: List[str] = Field(default=["*"], json_schema_extra={"example": ["*"]})
    api_jwt_public_key_path: str = "keys/public_key.pem"
    
    # Qdrant Configuration
    api_qdrant_url: str = "http://localhost:6333"
    api_qdrant_api_key: Optional[str] = None
    api_qdrant_collection_name: str = "lus_laboris_articles"
    
    # GCP Configuration
    api_gcp_project_id: Optional[str] = None
    api_google_application_credentials: Optional[str] = None
    api_gcp_use_credentials: bool = True
    
    # Embedding Configuration
    api_default_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    api_embedding_batch_size: int = 100
    api_embedding_device: str = "cpu"
    
    class Config:
        env_file = "../../.env"  # Search in the root project
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra variables from the .env


# Global settings instance
settings = Settings()
