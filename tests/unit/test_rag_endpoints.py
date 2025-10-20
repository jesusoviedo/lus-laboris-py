"""
Unit tests for RAG endpoints
"""

from unittest.mock import patch


def test_ask_question_returns_200(api_client):
    """Test POST /api/rag/ask returns 200"""
    with patch("api.services.rag_service.rag_service.answer_question") as mock_answer:
        # Mock the async answer_question method
        async def mock_answer_impl(*args, **kwargs):
            return {
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

        mock_answer.side_effect = mock_answer_impl

        payload = {"question": "¿Cuántos días de vacaciones corresponden?"}

        response = api_client.post("/api/rag/ask", json=payload)

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "answer" in response.json()
        assert "documents" in response.json()


def test_ask_question_validates_min_length(api_client):
    """Test POST /api/rag/ask validates minimum question length"""
    payload = {
        "question": "Hola"  # Too short (min 5 chars)
    }

    response = api_client.post("/api/rag/ask", json=payload)

    assert response.status_code == 422  # Validation error


def test_ask_question_validates_max_length(api_client):
    """Test POST /api/rag/ask validates maximum question length"""
    payload = {
        "question": "x" * 1001  # Too long (max 1000 chars)
    }

    response = api_client.post("/api/rag/ask", json=payload)

    assert response.status_code == 422  # Validation error


def test_ask_question_handles_error(api_client):
    """Test POST /api/rag/ask handles errors gracefully"""
    with patch("api.services.rag_service.rag_service.answer_question") as mock_answer:
        # Mock the service to return error response
        async def mock_error_impl(*args, **kwargs):
            return {
                "success": False,
                "question": "¿Cuántos días de vacaciones?",
                "answer": None,
                "error": "Collection test_collection does not exist",
                "processing_time_seconds": 0.1,
                "documents_retrieved": 0,
            }

        mock_answer.side_effect = mock_error_impl

        payload = {"question": "¿Cuántos días de vacaciones?"}

        response = api_client.post("/api/rag/ask", json=payload)

        # Should return 200 with success=False
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["success"] is False
        assert "error" in json_response
