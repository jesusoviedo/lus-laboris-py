"""
Unit tests for vectorstore endpoints
"""

from unittest.mock import patch


def test_get_collections_returns_200(api_client, mock_jwt_token):
    """Test GET /api/data/collections returns 200"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        with patch("api.services.qdrant_service.qdrant_service") as mock_qdrant:
            mock_qdrant.get_collections.return_value = ["legal_articles", "test_collection"]

            response = api_client.get(
                "/api/data/collections", headers={"Authorization": f"Bearer {mock_jwt_token}"}
            )

            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "collections" in response.json()


def test_get_collection_info_returns_200(api_client, mock_jwt_token):
    """Test GET /api/data/collections/{collection_name} returns 200"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        with (
            patch(
                "api.services.qdrant_service.qdrant_service.get_collection_info"
            ) as mock_get_info,
            patch("api.services.qdrant_service.qdrant_service.collection_exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_get_info.return_value = {
                "name": "legal_articles_test",
                "points_count": 413,
                "vector_size": 384,
                "distance_metric": "Cosine",
                "indexed_vectors_count": 413,
                "status": "green",
            }

            response = api_client.get(
                "/api/data/collections/legal_articles_test",
                headers={"Authorization": f"Bearer {mock_jwt_token}"},
            )

            assert response.status_code == 200
            assert response.json()["success"] is True
            assert response.json()["collection_name"] == "legal_articles_test"


def test_get_collection_info_not_found(api_client, mock_jwt_token):
    """Test GET /api/data/collections/{collection_name} returns 404 when not found"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        with patch("api.services.qdrant_service.qdrant_service") as mock_qdrant:
            mock_qdrant.get_collection_info.return_value = None

            response = api_client.get(
                "/api/data/collections/non_existent",
                headers={"Authorization": f"Bearer {mock_jwt_token}"},
            )

            assert response.status_code == 404


def test_delete_collection_returns_200(api_client, mock_jwt_token):
    """Test DELETE /api/data/collections/{collection_name} returns 200"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        with (
            patch("api.services.qdrant_service.qdrant_service.delete_collection") as mock_delete,
            patch("api.services.qdrant_service.qdrant_service.collection_exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_delete.return_value = True

            response = api_client.delete(
                "/api/data/collections/test_collection",
                headers={"Authorization": f"Bearer {mock_jwt_token}"},
            )

            assert response.status_code == 200
            assert response.json()["success"] is True


def test_load_to_vectorstore_local_returns_202(api_client, mock_jwt_token):
    """Test POST /api/data/load-to-vectorstore-local returns 202 (async job)"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        payload = {
            "filename": "codigo_trabajo_articulos.json",
            "local_data_path": "data/processed",
            "replace_collection": True,
        }

        response = api_client.post(
            "/api/data/load-to-vectorstore-local",
            json=payload,
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
        )

        assert response.status_code == 202
        assert response.json()["success"] is True
        assert "job_id" in response.json()


def test_load_to_vectorstore_local_requires_auth(api_client):
    """Test POST /api/data/load-to-vectorstore-local requires authentication"""
    payload = {
        "filename": "test.json",
        "local_data_path": "data/processed",
    }

    response = api_client.post("/api/data/load-to-vectorstore-local", json=payload)

    assert response.status_code == 403


def test_get_jobs_returns_200(api_client, mock_jwt_token):
    """Test GET /api/data/jobs returns 200"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        response = api_client.get(
            "/api/data/jobs", headers={"Authorization": f"Bearer {mock_jwt_token}"}
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "jobs" in response.json()
        assert "count" in response.json()


def test_get_jobs_requires_auth(api_client):
    """Test GET /api/data/jobs requires authentication"""
    response = api_client.get("/api/data/jobs")

    assert response.status_code == 403


def test_load_to_vectorstore_gcp_returns_202(api_client, mock_jwt_token):
    """Test POST /api/data/load-to-vectorstore-gcp returns 202 (async job)"""
    with patch("api.auth.jwt_handler.jwt_validator.validate_token") as mock_validate:
        mock_validate.return_value = {"username": "admin", "sub": "admin"}

        payload = {
            "filename": "codigo_trabajo_articulos.json",
            "folder": "processed",
            "bucket_name": "my-test-bucket",
            "replace_collection": True,
        }

        response = api_client.post(
            "/api/data/load-to-vectorstore-gcp",
            json=payload,
            headers={"Authorization": f"Bearer {mock_jwt_token}"},
        )

        assert response.status_code == 202
        assert response.json()["success"] is True
        assert "job_id" in response.json()


def test_load_to_vectorstore_gcp_requires_auth(api_client):
    """Test POST /api/data/load-to-vectorstore-gcp requires authentication"""
    payload = {
        "filename": "test.json",
        "folder": "processed",
        "bucket_name": "my-bucket",
    }

    response = api_client.post("/api/data/load-to-vectorstore-gcp", json=payload)

    assert response.status_code == 403
