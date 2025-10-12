"""
Configuration settings for the API
"""

import logging
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    api_log_level: str = "info"

    # Security
    api_allowed_origins: list[str] = Field(default=["*"], json_schema_extra={"example": ["*"]})
    api_allowed_hosts: list[str] = Field(default=["*"], json_schema_extra={"example": ["*"]})
    api_jwt_public_key_path: str = None
    api_jwt_aud: str = "lus-laboris-client"
    api_jwt_iss: str = "lus-laboris-api"

    # Qdrant Configuration
    api_qdrant_url: str = None
    api_qdrant_api_key: str | None = None
    api_qdrant_collection_name: str = None
    api_qdrant_grpc_port: int = 6334  # Puerto gRPC de Qdrant (default: 6334)
    api_qdrant_prefer_grpc: bool = True  # Preferir gRPC sobre HTTP (más rápido)

    # GCP Configuration
    api_gcp_project_id: str | None = None
    api_google_application_credentials: str | None = None
    api_gcp_use_credentials: bool = False

    # Embedding Configuration
    api_embedding_model: str = None
    api_embedding_batch_size: int = 100

    # Reranking Configuration
    api_reranking_model: str = None
    api_use_reranking: bool = False

    # RAG Configuration
    api_rag_top_k: int = None
    api_llm_provider: str = None
    api_llm_model: str = None

    # LLM API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    # Rate Limiting
    api_rate_limit_requests: int = 10
    api_rate_limit_window: str = "1 minute"

    # Debug Configuration
    api_debug_config: bool = False

    # Phoenix Monitoring Configuration
    api_phoenix_enabled: bool = True
    api_phoenix_endpoint: str | None = None
    api_phoenix_grpc_endpoint: str | None = "localhost:4317"
    api_phoenix_use_grpc: bool = True
    api_phoenix_api_key: str | None = None
    api_phoenix_project_name: str = "lus-laboris-api"

    # Environment Configuration
    api_environment: str = "development"

    class Config:
        project_root = Path(__file__).parent.parent.parent.parent
        path_env_file_default = project_root / ".env"

        # Get the environment file path from the environment variable or use the default
        # Convert to Path to ensure consistency
        env_file_path = os.getenv("API_ENV_FILE_PATH", path_env_file_default)
        env_file = Path(env_file_path) if isinstance(env_file_path, str) else env_file_path
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra variables from the .env


# Global settings instance
settings = Settings()

# Log which .env file is being used
logger.info(f"Using .env file: {settings.Config.env_file}")

# Optional: Debug information
if settings.api_debug_config:
    logger.info(f"File exists: {settings.Config.env_file.exists()}")
    logger.info(f"Project root: {settings.Config.project_root}")
