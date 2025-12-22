"""Tests for text preprocessing."""

import pytest

from rag_pipeline.preprocessor import TextPreprocessor, count_tokens


def test_count_tokens():
    """Test token counting."""
    text = "Hello world, this is a test sentence."
    count = count_tokens(text)
    assert count > 0
    assert isinstance(count, int)


def test_text_normalization():
    """Test text normalization."""
    preprocessor = TextPreprocessor({"min_tokens": 100, "target_tokens": 350, "max_tokens": 512})

    text = "Hello  world\n\n\n\nthis   is  a  test"
    normalized = preprocessor.normalize_text(text)

    assert "  " not in normalized  # No double spaces
    assert "\n\n\n" not in normalized  # No excessive newlines


def test_boilerplate_removal():
    """Test boilerplate removal."""
    preprocessor = TextPreprocessor({"min_tokens": 100, "target_tokens": 350, "max_tokens": 512})

    text = """
    Main content here.

    Edit this page
    https://example.com/edit

    Previous: Chapter 1
    Next: Chapter 3

    More content.
    """

    cleaned = preprocessor.remove_boilerplate(text)
    assert "Edit this page" not in cleaned
    assert "Previous:" not in cleaned


def test_semantic_boundary_detection():
    """Test semantic boundary detection."""
    preprocessor = TextPreprocessor({"min_tokens": 100, "target_tokens": 350, "max_tokens": 512})

    text = """First paragraph.

Second paragraph.

## Section Header

Third paragraph.
"""

    boundaries = preprocessor.find_semantic_boundaries(text)
    assert len(boundaries) > 1
    assert boundaries[0] == 0


def test_chunking():
    """Test text chunking."""
    preprocessor = TextPreprocessor(
        {
            "min_tokens": 10,
            "target_tokens": 50,
            "max_tokens": 100,
            "overlap_tokens": 10,
        }
    )

    text = "A" * 500  # Large text that needs chunking

    chunks = preprocessor.chunk_text(text)
    assert len(chunks) > 1

    # Each chunk should be within limits
    for chunk in chunks:
        token_count = count_tokens(chunk)
        assert token_count <= 100


def test_chunk_id_generation():
    """Test chunk ID generation."""
    preprocessor = TextPreprocessor({"min_tokens": 100, "target_tokens": 350, "max_tokens": 512})

    chunk_id = preprocessor.generate_chunk_id(
        "https://example.com/docs/module-1-intro", 0, 0
    )

    assert chunk_id.startswith("chunk_")
    assert "mod" in chunk_id
