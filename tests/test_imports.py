"""Test that all modules are importable."""

import pytest


def test_imports():
    """Test that all rag_pipeline modules can be imported."""
    try:
        from rag_pipeline import __version__
        from rag_pipeline.config import Config
        from rag_pipeline.logging_utils import get_logger
        from rag_pipeline.crawler import DocumentationCrawler
        from rag_pipeline.preprocessor import TextPreprocessor
        from rag_pipeline.embeddings import CohereEmbeddingsGenerator
        from rag_pipeline.storage import QdrantVectorStore
        from rag_pipeline.verification import RAGVerifier
        from rag_pipeline.utils.retry import ExponentialBackoff
        from rag_pipeline.utils.text_processing import normalize_whitespace

        assert __version__ == "0.1.0"
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


def test_logger_creation():
    """Test logger creation."""
    from rag_pipeline.logging_utils import get_logger

    logger = get_logger()
    assert logger is not None


def test_exponential_backoff():
    """Test exponential backoff calculation."""
    from rag_pipeline.utils.retry import ExponentialBackoff

    backoff = ExponentialBackoff(initial_delay=1, max_attempts=3)
    assert backoff.get_next_delay() == 1.0  # 1 * 2^0
    backoff.wait()
    assert backoff.get_next_delay() == 2.0  # 1 * 2^1
    backoff.wait()
    assert backoff.get_next_delay() == 4.0  # 1 * 2^2
