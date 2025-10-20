"""
Pytest configuration and shared fixtures for testing.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src/lus_laboris_api to Python path
# This allows importing from the API package without installing it as a package
api_path = Path(__file__).parent.parent / "src" / "lus_laboris_api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("API_HOST", "0.0.0.0")
    monkeypatch.setenv("API_PORT", "8000")
    monkeypatch.setenv("API_RELOAD", "false")
    monkeypatch.setenv("API_LOG_LEVEL", "info")
    monkeypatch.setenv("API_QDRANT_URL", "http://localhost:6333")
    monkeypatch.setenv("API_QDRANT_COLLECTION_NAME", "test_collection")
    monkeypatch.setenv("API_DEFAULT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    monkeypatch.setenv("API_EMBEDDING_BATCH_SIZE", "100")
    monkeypatch.setenv("API_JWT_PUBLIC_KEY_PATH", "keys/public_key.pem")
    monkeypatch.setenv("API_ALLOWED_ORIGINS", '["*"]')
    monkeypatch.setenv("API_ALLOWED_HOSTS", '["*"]')
    monkeypatch.setenv("API_PHOENIX_ENABLED", "false")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")


@pytest.fixture
def api_client(mock_env_vars):
    """Create a test client for the FastAPI application."""
    # Import here to ensure env vars are set
    # Now we can import directly because we added the path above
    from api.main import app

    return TestClient(app)


@pytest.fixture
def sample_legal_article():
    """Sample legal article for testing."""
    return {
        "article_number": "1",
        "title": "Objeto del Código",
        "content": "El presente Código regula las relaciones entre el capital y el trabajo...",
        "book": "Libro Primero",
        "chapter": "Capítulo I",
        "metadata": {"source": "Ley Nº 213", "country": "Paraguay"},
    }


@pytest.fixture
def sample_query():
    """Sample user query for testing."""
    return "¿Cuántos días de vacaciones corresponden por año?"


@pytest.fixture
def sample_embedding():
    """Sample embedding vector for testing."""
    import numpy as np

    return np.random.rand(384).tolist()  # 384-dimensional vector


@pytest.fixture
def mock_qdrant_response():
    """Mock Qdrant search response."""
    return {
        "results": [
            {
                "id": "1",
                "score": 0.95,
                "payload": {
                    "article_number": "154",
                    "content": "Todo trabajador tiene derecho a un período de vacaciones...",
                    "book": "Libro Segundo",
                    "chapter": "Capítulo VIII",
                },
            }
        ]
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "answer": "Según el Código del Trabajo de Paraguay, todo trabajador tiene derecho...",
        "sources": ["Artículo 154"],
        "confidence": 0.95,
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for authentication."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWRtaW4ifQ.mock_signature"


@pytest.fixture
def mock_qdrant_service(monkeypatch):
    """Mock Qdrant service responses."""
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    mock_service.health_check.return_value = {
        "status": "healthy",
        "url": "http://localhost:6333",
        "collections_count": 2,
    }
    mock_service.get_collections.return_value = ["legal_articles_test", "test_collection"]
    mock_service.collection_exists.return_value = True
    mock_service.get_collection_info.return_value = {
        "name": "legal_articles_test",
        "points_count": 413,
        "vector_size": 384,
        "distance": "Cosine",
        "status": "green",
    }

    return mock_service


@pytest.fixture
def mock_embedding_service(monkeypatch):
    """Mock Embedding service."""
    from unittest.mock import MagicMock

    import numpy as np

    mock_service = MagicMock()
    mock_service.health_check.return_value = {
        "status": "healthy",
        "default_model": "intfloat/multilingual-e5-small",
        "device": "cpu",
        "loaded_models": ["intfloat/multilingual-e5-small"],
        "model_dimensions": 384,
    }
    mock_service.embed_texts.return_value = (np.random.rand(5, 384), {"model": "test"})

    return mock_service


@pytest.fixture
def mock_rag_service(monkeypatch):
    """Mock RAG service."""
    from unittest.mock import AsyncMock

    mock_service = AsyncMock()
    mock_service.answer_question.return_value = {
        "success": True,
        "question": "¿Cuántos días de vacaciones?",
        "answer": "Según el Artículo 218, son 12 días hábiles por año.",
        "documents": [
            {
                "id": 218,
                "score": 0.95,
                "content": "Artículo 218: Todo trabajador tiene derecho a 12 días hábiles...",
            }
        ],
        "session_id": "test-session-123",
        "processing_time_seconds": 1.5,
        "documents_retrieved": 5,
        "top_k": 5,
        "reranking_applied": True,
    }

    return mock_service
