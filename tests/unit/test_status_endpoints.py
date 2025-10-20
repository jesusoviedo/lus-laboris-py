"""
Unit tests for status and root endpoints
"""

from unittest.mock import patch


def test_root_endpoint_returns_200(api_client):
    """Test GET / returns 200"""
    response = api_client.get("/")

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "version" in response.json()
    assert "docs_url" in response.json()
    assert "health_check" in response.json()


def test_root_endpoint_has_correct_urls(api_client):
    """Test GET / returns correct URLs"""
    response = api_client.get("/")

    json_response = response.json()
    assert json_response["docs_url"] == "/docs"
    assert json_response["health_check"] == "/api/health"


def test_status_endpoint_returns_200(api_client):
    """Test GET /api/status returns 200 (without auth)"""
    with (
        patch("api.services.qdrant_service.qdrant_service") as mock_qdrant,
        patch("api.services.embedding_service.embedding_service") as mock_embedding,
    ):
        mock_qdrant.health_check.return_value = {"status": "healthy"}
        mock_embedding.health_check.return_value = {"status": "healthy"}

        response = api_client.get("/api/status")

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "services" in response.json()


def test_status_endpoint_shows_services(api_client):
    """Test GET /api/status shows service statuses"""
    with (
        patch("api.services.qdrant_service.qdrant_service") as mock_qdrant,
        patch("api.services.embedding_service.embedding_service") as mock_embedding,
        patch("api.services.gcp_service.gcp_service") as mock_gcp,
    ):
        mock_qdrant.health_check.return_value = {"status": "healthy", "collections_count": 2}
        mock_embedding.health_check.return_value = {"status": "healthy", "default_model": "test"}
        mock_gcp.health_check.return_value = {"status": "healthy"}

        response = api_client.get("/api/status")

        json_response = response.json()
        assert "services" in json_response
        services = json_response["services"]

        # Verify service keys exist
        assert "qdrant" in services
        assert "embedding_service" in services
