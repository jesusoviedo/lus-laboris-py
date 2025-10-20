"""
Unit tests for health check endpoints.
"""

from unittest.mock import patch

import pytest


def test_health_endpoint_returns_200(api_client):
    """Test that health endpoint returns 200 OK."""
    response = api_client.get("/api/health")
    assert response.status_code == 200


def test_health_endpoint_returns_json(api_client):
    """Test that health endpoint returns JSON response."""
    response = api_client.get("/api/health")
    assert response.headers["content-type"] == "application/json"


def test_health_endpoint_has_status_field(api_client):
    """Test that health endpoint response has status field."""
    response = api_client.get("/api/health")
    data = response.json()
    assert "status" in data


def test_ready_endpoint_returns_200(api_client):
    """Test that ready endpoint returns 200 OK."""
    response = api_client.get("/api/health/ready")
    assert response.status_code == 200


@pytest.mark.integration
def test_qdrant_health_check(api_client):
    """Test Qdrant health check endpoint."""
    response = api_client.get("/api/health/qdrant")
    # This might fail if Qdrant is not running, so we just check the endpoint exists
    assert response.status_code in [200, 503]


def test_docs_endpoint_accessible(api_client):
    """Test that Swagger docs are accessible."""
    response = api_client.get("/docs")
    assert response.status_code == 200


def test_gcp_health_check(api_client):
    """Test GET /api/health/gcp returns GCP status"""
    with patch("api.services.gcp_service.gcp_service") as mock_gcp:
        mock_gcp.health_check.return_value = {
            "status": "healthy",
            "buckets_count": 2,
        }

        response = api_client.get("/api/health/gcp")

        assert response.status_code == 200
        assert "status" in response.json()


def test_embeddings_health_check(api_client):
    """Test GET /api/health/embeddings returns embedding service status"""
    with patch("api.services.embedding_service.embedding_service") as mock_embedding:
        mock_embedding.health_check.return_value = {
            "status": "healthy",
            "default_model": "intfloat/multilingual-e5-small",
            "device": "cpu",
        }

        response = api_client.get("/api/health/embeddings")

        assert response.status_code == 200
        assert "status" in response.json()


def test_reranking_health_check(api_client):
    """Test GET /api/health/reranking returns reranking service status"""
    with patch("api.services.reranking_service.reranking_service") as mock_reranking:
        mock_reranking.health_check.return_value = {
            "status": "healthy",
            "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        }

        response = api_client.get("/api/health/reranking")

        assert response.status_code == 200
        assert "status" in response.json()


def test_rag_health_check(api_client):
    """Test GET /api/health/rag returns RAG service status"""
    with patch("api.services.rag_service.rag_service") as mock_rag:
        mock_rag.health_check.return_value = {
            "status": "healthy",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
        }

        response = api_client.get("/api/health/rag")

        assert response.status_code == 200
        assert "status" in response.json()


def test_phoenix_health_check(api_client):
    """Test GET /api/health/phoenix returns Phoenix monitoring status"""
    response = api_client.get("/api/health/phoenix")

    # Phoenix health check doesn't require mocking, it checks env vars
    assert response.status_code == 200
    assert "status" in response.json()
