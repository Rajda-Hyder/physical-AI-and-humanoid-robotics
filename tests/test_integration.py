"""Integration tests for RAG pipeline."""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pytest


def test_config_loading():
    """Test configuration loading."""
    from rag_pipeline.config import Config

    # Create temp .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("COHERE_API_KEY=test-key\n")
        f.write("QDRANT_URL=https://test.qdrant.io\n")
        f.write("QDRANT_API_KEY=test-api-key\n")
        f.write("TARGET_WEBSITE_URL=https://example.com/docs\n")
        env_file = f.name

    try:
        config = Config(env_file=env_file)

        assert config.cohere_api_key == "test-key"
        assert config.qdrant_url == "https://test.qdrant.io"
        assert config.target_website_url == "https://example.com/docs"
    finally:
        Path(env_file).unlink()


def test_text_chunk_creation():
    """Test creating text chunks."""
    from rag_pipeline.preprocessor import TextChunk
    from datetime import datetime

    chunk = TextChunk(
        chunk_id="test-chunk-001",
        source_url="https://example.com/page",
        module="Module 1",
        section="Introduction",
        text="This is test content for embedding.",
        token_count=8,
        chunk_index=0,
        total_chunks=1,
        created_at=datetime.utcnow(),
    )

    assert chunk.chunk_id == "test-chunk-001"
    assert chunk.token_count == 8
    assert chunk.module == "Module 1"


def test_full_text_processing_pipeline():
    """Test complete text processing pipeline."""
    from rag_pipeline.preprocessor import TextPreprocessor
    from rag_pipeline.crawler import CrawlResult

    # Create mock crawl result
    result = CrawlResult(
        url="https://example.com/docs/intro",
        title="Introduction to AI",
        module="Module 1: Foundations",
        section="Getting Started",
        html_content="<html><body>Test content</body></html>",
        text_content="""
        Introduction to Artificial Intelligence

        This is the first section about AI basics.

        ## Core Concepts

        Here are the main concepts you need to know.

        ## Applications

        AI has many practical applications in industry.
        """,
        crawled_at=datetime.utcnow(),
        page_type="documentation",
        hierarchy_level=2,
    )

    # Process with preprocessor
    config = {
        "min_tokens": 10,
        "target_tokens": 50,
        "max_tokens": 100,
        "overlap_tokens": 5,
    }
    preprocessor = TextPreprocessor(config)

    chunks = preprocessor.preprocess_crawled_content([result])

    assert len(chunks) > 0
    assert all(isinstance(c, type(chunks[0])) for c in chunks)
    assert all(c.source_url == result.url for c in chunks)
    assert all(c.module == result.module for c in chunks)


def test_output_file_generation():
    """Test that output files are generated correctly."""
    from rag_pipeline.main import save_crawl_results, save_chunks_to_file
    from rag_pipeline.crawler import CrawlResult
    from rag_pipeline.preprocessor import TextChunk

    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test crawl result
        result = CrawlResult(
            url="https://example.com/docs/test",
            title="Test Page",
            module="Test Module",
            section="Test Section",
            html_content="<html></html>",
            text_content="Test content",
            crawled_at=datetime.utcnow(),
            page_type="documentation",
            hierarchy_level=1,
        )

        # Save crawl results
        crawl_file = save_crawl_results([result], output_dir=tmpdir)
        assert Path(crawl_file).exists()

        # Verify JSON content
        with open(crawl_file) as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["title"] == "Test Page"

        # Create test chunk
        chunk = TextChunk(
            chunk_id="test-001",
            source_url="https://example.com",
            module="Test",
            section="Introduction",
            text="Test chunk content",
            token_count=4,
            chunk_index=0,
            total_chunks=1,
            created_at=datetime.utcnow(),
        )

        # Save chunks
        chunks_file = save_chunks_to_file([chunk], output_dir=tmpdir, format="json")
        assert Path(chunks_file).exists()

        # Verify JSON content
        with open(chunks_file) as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["chunk_id"] == "test-001"


def test_logging_functionality():
    """Test logging system."""
    import logging
    from rag_pipeline.logging_utils import get_logger

    logger = get_logger()

    # Test that logger methods exist and are callable
    assert callable(logger.log_info)
    assert callable(logger.log_error)
    assert callable(logger.log_warning)
    assert callable(logger.log_debug)
    assert callable(logger.log_operation)

    # Test logging operations
    with tempfile.TemporaryDirectory() as tmpdir:
        logger2 = get_logger()  # Get new logger
        logger2.log_operation("test_operation", {"test_key": "test_value"})

        # Check if operations log was created
        assert logger2.ops_log_file is not None


@pytest.mark.skip(reason="Requires actual Qdrant and Cohere instances")
def test_end_to_end_pipeline():
    """Test complete end-to-end pipeline (requires APIs)."""
    from rag_pipeline.main import run_pipeline

    result = run_pipeline(verify_only=True)

    assert result["success"]
    assert "crawled_pages" in result
    assert "created_chunks" in result
    assert "report_file" in result


def test_exponential_backoff_retry():
    """Test exponential backoff retry logic."""
    from rag_pipeline.utils.retry import ExponentialBackoff

    backoff = ExponentialBackoff(initial_delay=1, max_attempts=3, base=2)

    delays = []
    for _ in range(3):
        delays.append(backoff.get_next_delay())
        backoff.wait()

    # Should be: 1, 2, 4
    assert delays[0] == 1.0
    assert delays[1] == 2.0
    assert delays[2] == 4.0


def test_text_utilities():
    """Test text processing utilities."""
    from rag_pipeline.utils.text_processing import (
        normalize_whitespace,
        remove_extra_newlines,
        is_code_block,
    )

    # Test whitespace normalization
    text = "Hello  world\n\ntest"
    normalized = normalize_whitespace(text)
    assert "  " not in normalized

    # Test newline removal
    text_with_newlines = "Line 1\n\n\n\nLine 2"
    cleaned = remove_extra_newlines(text_with_newlines)
    assert cleaned.count("\n") <= 1

    # Test code block detection
    code = "def hello():\n    print('world')"
    assert is_code_block(code)

    regular = "This is regular text without code"
    assert not is_code_block(regular)
