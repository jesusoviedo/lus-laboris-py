"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from fastapi.testclient import TestClient


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


@pytest.fixture
def api_client(mock_env_vars):
    """Create a test client for the FastAPI application."""
    # Import here to ensure env vars are set
    from lus_laboris_api.api.main import app

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
