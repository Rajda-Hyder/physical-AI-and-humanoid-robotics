"""Text processing utilities for RAG pipeline."""

import re
from typing import List


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.

    Converts multiple spaces to single space and standardizes line breaks.
    """
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r"\n\n+", "\n\n", text)
    # Replace tabs with spaces
    text = text.replace("\t", "  ")
    return text.strip()


def remove_extra_newlines(text: str) -> str:
    """Remove excessive newlines while preserving paragraph structure."""
    lines = text.split("\n")
    # Remove empty lines
    non_empty = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty)


def extract_text_from_markdown(text: str) -> str:
    """
    Extract plain text from markdown-formatted content.

    Preserves structure markers but removes markdown syntax.
    """
    # Keep heading markers but remove extra markdown syntax
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **bold** -> bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # *italic* -> italic
    text = re.sub(r"__(.*?)__", r"\1", text)  # __bold__ -> bold
    text = re.sub(r"_(.*?)_", r"\1", text)  # _italic_ -> italic
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # [link](url) -> link

    return text


def is_code_block(text: str) -> bool:
    """Detect if text appears to be a code block."""
    # Check for common code indicators
    code_patterns = [
        r"^```",  # Markdown code fence
        r"^    ",  # Indented code
        r"def\s+\w+\(",  # Python function
        r"function\s+\w+\(",  # JavaScript function
        r"class\s+\w+",  # Class definition
    ]
    for pattern in code_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False
