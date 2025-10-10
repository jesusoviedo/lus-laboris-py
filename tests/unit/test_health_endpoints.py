"""
Unit tests for health check endpoints.
"""

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
