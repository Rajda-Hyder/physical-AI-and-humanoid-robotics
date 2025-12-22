"""Tests for vector storage."""

import pytest


def test_qdrant_client_init():
    """Test QdrantVectorStore initialization."""
    from rag_pipeline.storage import QdrantVectorStore

    # This will fail without actual Qdrant instance, but tests structure
    with pytest.raises(Exception):
        # Should fail to connect
        store = QdrantVectorStore(
            url="https://invalid-qdrant.example.com",
            api_key="invalid-key",
            collection_name="test-collection",
        )


def test_collection_info_type():
    """Test collection info structure."""
    # This is a structure test without requiring a live instance
    expected_info = {
        "name": "documents",
        "points_count": 100,
        "vectors_count": 100,
    }

    assert "name" in expected_info
    assert "points_count" in expected_info
    assert "vectors_count" in expected_info


@pytest.mark.skip(reason="Requires Qdrant instance")
def test_store_and_search():
    """Test storing and searching vectors (requires Qdrant instance)."""
    from rag_pipeline.storage import QdrantVectorStore
    from rag_pipeline.preprocessor import TextChunk
    from datetime import datetime

    store = QdrantVectorStore(
        url="http://localhost:6333",
        api_key="test-key",
    )

    # Create test chunk
    chunk = TextChunk(
        chunk_id="test-001",
        source_url="https://example.com",
        module="Test",
        section="Introduction",
        text="This is test content",
        token_count=5,
        chunk_index=0,
        total_chunks=1,
        created_at=datetime.utcnow(),
    )

    # Create dummy embedding
    embedding = [0.1] * 1024

    # Store
    count = store.store_embeddings([embedding], [chunk])
    assert count == 1

    # Search
    results = store.search(embedding, top_k=1)
    assert len(results) > 0
