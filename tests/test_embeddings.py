"""Tests for embeddings generation."""

import pytest


def test_cohere_embeddings_init():
    """Test CohereEmbeddingsGenerator initialization."""
    from rag_pipeline.embeddings import CohereEmbeddingsGenerator

    generator = CohereEmbeddingsGenerator(api_key="test-key", model="embed-english-v3.0")

    assert generator.api_key == "test-key"
    assert generator.model == "embed-english-v3.0"
    assert generator.embedding_dimension == 1024


def test_embedding_dimension():
    """Test getting embedding dimension."""
    from rag_pipeline.embeddings import CohereEmbeddingsGenerator

    generator = CohereEmbeddingsGenerator(api_key="test-key")

    assert generator.get_embedding_dimension() == 1024


@pytest.mark.skip(reason="Requires Cohere API key")
def test_generate_embeddings():
    """Test generating embeddings (requires API key)."""
    from rag_pipeline.embeddings import CohereEmbeddingsGenerator

    generator = CohereEmbeddingsGenerator(api_key="your-api-key")

    texts = ["Hello world", "How are you?"]
    embeddings = generator.generate_embeddings(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1024
