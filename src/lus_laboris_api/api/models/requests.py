"""
Pydantic models for API requests
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoadToVectorstoreLocalRequest(BaseModel):
    """Request model for loading data to vectorstore from local files"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "codigo_trabajo_articulos.json",
                "local_data_path": "data/processed",
                "replace_collection": False,
            }
        }
    )

    filename: str = Field(
        ..., description="Name of the JSON file to load (without path)", min_length=1
    )

    local_data_path: str | None = Field(
        None,
        description="Path to the data directory (relative to project root). Default: 'data/processed'",
    )

    # Optional parameters
    replace_collection: bool = Field(
        False, description="Whether to replace existing collection if it exists"
    )


class LoadToVectorstoreGCPRequest(BaseModel):
    """Request model for loading data to vectorstore from GCS"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "codigo_trabajo_articulos.json",
                "folder": "processed",
                "bucket_name": "mi-bucket",
                "replace_collection": False,
            }
        }
    )

    filename: str = Field(
        ..., description="Name of the JSON file to load (without path)", min_length=1
    )

    folder: str = Field(
        ..., description="Folder path in the GCS bucket where the file is located", min_length=1
    )

    bucket_name: str = Field(..., description="Name of the GCS bucket", min_length=1)

    # Optional parameters
    replace_collection: bool = Field(
        False, description="Whether to replace existing collection if it exists"
    )


# Legacy model for backward compatibility
class LoadToVectorstoreRequest(BaseModel):
    """Request model for loading data to vectorstore (legacy)"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mode": "local",
                "filename": "codigo_trabajo_articulos.json",
                "collection_name": "labor_law_articles",
                "local_data_path": "data/processed",
                "batch_size": 100,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "replace_collection": False,
            }
        }
    )

    mode: Literal["local", "gcp"] = Field(
        ...,
        description="Mode for loading data: 'local' for local files or 'gcp' for Google Cloud Storage",
    )

    # Common fields
    filename: str = Field(
        ..., description="Name of the JSON file to load (without path)", min_length=1
    )

    collection_name: str | None = Field(
        None, description="Name of the Qdrant collection. If not provided, will be auto-generated"
    )

    # Local mode fields
    local_data_path: str | None = Field(
        None,
        description="Path to the data directory (relative to project root). Default: 'data/processed'",
    )

    # GCP mode fields
    bucket_name: str | None = Field(
        None, description="Name of the GCS bucket (required for GCP mode)"
    )

    gcp_credentials_path: str | None = Field(
        None, description="Path to GCP credentials JSON file (required when running locally)"
    )

    # Optional parameters
    batch_size: int = Field(
        100, description="Number of documents to process in each batch", ge=1, le=1000
    )

    embedding_model: str | None = Field(
        None, description="Name of the embedding model to use. If not provided, will use default"
    )

    replace_collection: bool = Field(
        False, description="Whether to replace existing collection if it exists"
    )


class QuestionRequest(BaseModel):
    """Request model for asking questions to the RAG system"""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"question": "¿Cuáles son los derechos del trabajador en caso de despido?"}
        }
    )

    question: str = Field(
        ...,
        description="The question to ask about Paraguayan labor law",
        min_length=5,
        max_length=1000,
    )
