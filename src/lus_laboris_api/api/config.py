"""
Configuration settings for the API
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path


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
    api_jwt_public_key_path: str = None
    
    # Qdrant Configuration
    api_qdrant_url: str = None
    api_qdrant_api_key: Optional[str] = None
    api_qdrant_collection_name: str = None
    
    # GCP Configuration
    api_gcp_project_id: Optional[str] = None
    api_google_application_credentials: Optional[str] = None
    api_gcp_use_credentials: bool = False
    
    # Embedding Configuration
    api_default_embedding_model: str = None
    api_embedding_batch_size: int = 100
    
    class Config:
        project_root = Path(__file__).parent.parent.parent.parent
        path_env_file_default = project_root / ".env"

        # Get the environment file path from the environment variable or use the default
        env_file = os.getenv("API_ENV_FILE_PATH", path_env_file_default)
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra variables from the .env

            # Optional: Log which .env file is being used
        if os.getenv("DEBUG_CONFIG", "false").lower() == "true":
            print(f"Using .env file: {env_file}")
            print(f"File exists: {env_file.exists()}")
        

# Global settings instance
settings = Settings()
