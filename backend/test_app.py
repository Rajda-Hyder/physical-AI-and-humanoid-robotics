"""Tests for RAG Chatbot backend."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.app import app
from backend.services import RAGService, QdrantService


@pytest.fixture
def mock_services():
    """Create mock services for testing."""
    mock_qdrant = MagicMock(spec=QdrantService)
    mock_qdrant.health_check.return_value = True
    mock_qdrant.get_collection_info.return_value = {
        "name": "documents",
        "points_count": 100,
        "vectors_count": 100,
    }
    mock_qdrant.search.return_value = [
        {
            "chunk_id": "chunk_001",
            "score": 0.95,
            "text": "Sample content about Physical AI",
            "source_url": "https://example.com/docs",
            "module": "Module 1",
            "section": "Foundations",
        }
    ]

    mock_rag = MagicMock(spec=RAGService)
    mock_rag.model = "embed-english-v3.0"
    mock_rag.qdrant_service = mock_qdrant
    mock_rag.health_check.return_value = {
        "status": "healthy",
        "cohere": "connected",
        "qdrant": "connected",
        "model": "embed-english-v3.0",
    }
    mock_rag.query.return_value = {
        "question": "What is Physical AI?",
        "context": "## Context\nSample content",
        "sources": [
            {
                "url": "https://example.com/docs",
                "section": "Foundations",
                "score": 0.95,
            }
        ],
        "metadata": {
            "model": "embed-english-v3.0",
            "context_chunks": 1,
            "query_succeeded": True,
        },
    }

    return mock_rag, mock_qdrant


@pytest.fixture
def client(mock_services):
    """Create test client with mock services."""
    from backend.api.routes import set_rag_service

    mock_rag, _ = mock_services
    set_rag_service(mock_rag)

    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "RAG Chatbot API" in response.json()["name"]


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["cohere"] == "connected"
    assert data["qdrant"] == "connected"


def test_service_info(client):
    """Test service info endpoint."""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "RAG Chatbot API"
    assert data["model"] == "embed-english-v3.0"


def test_query_success(client):
    """Test successful query."""
    payload = {
        "question": "What is Physical AI?",
        "top_k": 5,
        "include_context": True,
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is Physical AI?"
    assert "context" in data
    assert "sources" in data
    assert len(data["sources"]) > 0


def test_query_short_question(client):
    """Test query with too short question."""
    payload = {"question": "AI"}
    response = client.post("/api/query", json=payload)
    assert response.status_code == 400


def test_query_empty_question(client):
    """Test query with empty question."""
    payload = {"question": ""}
    response = client.post("/api/query", json=payload)
    assert response.status_code == 400


def test_query_parameters(client):
    """Test query with different parameters."""
    payload = {
        "question": "Tell me about embeddings",
        "top_k": 10,
        "include_context": False,
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "Tell me about embeddings"


def test_query_response_structure(client):
    """Test query response structure."""
    payload = {"question": "What is Qdrant?"}
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "question" in data
    assert "context" in data
    assert "sources" in data
    assert "metadata" in data

    # Check metadata
    assert data["metadata"]["model"] == "embed-english-v3.0"
    assert data["metadata"]["context_chunks"] >= 0
    assert "query_succeeded" in data["metadata"]


def test_source_format(client):
    """Test source format in response."""
    payload = {"question": "What is RAG?"}
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    sources = data["sources"]
    assert len(sources) > 0

    source = sources[0]
    assert "url" in source
    assert "section" in source
    assert "score" in source
    assert isinstance(source["score"], (int, float))
    assert 0 <= source["score"] <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
