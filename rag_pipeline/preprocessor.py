"""Text preprocessing and chunking for RAG pipeline."""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import tiktoken

from .logging_utils import get_logger
from .utils.text_processing import normalize_whitespace, remove_extra_newlines


def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model("gpt-2")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        # Fallback: estimate 1 token per 4 characters
        return len(text) // 4


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    chunk_id: str
    source_url: str
    module: str
    section: str
    text: str
    token_count: int
    chunk_index: int
    total_chunks: int
    created_at: datetime


class TextPreprocessor:
    """Preprocesses and chunks text for embedding generation."""

    def __init__(self, config: Dict):
        """Initialize preprocessor."""
        self.config = config
        self.logger = get_logger()
        self.min_tokens = config.get("min_tokens", 100)
        self.target_tokens = config.get("target_tokens", 350)
        self.max_tokens = config.get("max_tokens", 512)
        self.overlap_tokens = config.get("overlap_tokens", 50)

    def normalize_text(self, text: str) -> str:
        """Normalize text for processing."""
        text = normalize_whitespace(text)
        text = remove_extra_newlines(text)
        return text

    def remove_boilerplate(self, text: str) -> str:
        """Remove common boilerplate elements."""
        # Remove "Edit this page" links
        text = re.sub(r"Edit\s+this\s+page.*?\n", "", text, flags=re.IGNORECASE)
        # Remove "Previous/Next" navigation
        text = re.sub(r"(?:Previous|Next):.*?\n", "", text, flags=re.IGNORECASE)
        # Remove "On this page" sections
        text = re.sub(r"On\s+this\s+page.*?\n", "", text, flags=re.IGNORECASE)
        return text

    def find_semantic_boundaries(self, text: str) -> List[int]:
        """Find semantic boundaries in text (paragraphs, sections)."""
        boundaries = [0]

        # Find paragraph breaks (double newlines)
        for match in re.finditer(r"\n\n+", text):
            boundaries.append(match.start())

        # Find section headers
        for match in re.finditer(r"^#+\s", text, re.MULTILINE):
            boundaries.append(match.start())

        # Find code block boundaries
        in_code_block = False
        for match in re.finditer(r"^```", text, re.MULTILINE):
            if in_code_block:
                boundaries.append(match.end())
            in_code_block = not in_code_block

        boundaries.append(len(text))
        return sorted(list(set(boundaries)))

    def split_at_boundaries(self, text: str, boundaries: List[int]) -> List[str]:
        """Split text at semantic boundaries."""
        sections = []
        for i in range(len(boundaries) - 1):
            section = text[boundaries[i] : boundaries[i + 1]].strip()
            if section:
                sections.append(section)
        return sections

    def chunk_text(
        self,
        text: str,
        min_tokens: Optional[int] = None,
        target_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
        overlap_tokens: Optional[int] = None,
    ) -> List[str]:
        """Chunk text intelligently with semantic boundaries."""
        min_tokens = min_tokens or self.min_tokens
        target_tokens = target_tokens or self.target_tokens
        max_tokens = max_tokens or self.max_tokens
        overlap_tokens = overlap_tokens or self.overlap_tokens

        # Find semantic boundaries
        boundaries = self.find_semantic_boundaries(text)
        sections = self.split_at_boundaries(text, boundaries)

        chunks = []
        current_chunk = ""
        current_tokens = 0

        for section in sections:
            section_tokens = count_tokens(section)

            # If section itself is too large, split it
            if section_tokens > max_tokens:
                # Add current chunk if not empty
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_tokens = 0

                # Split large section by sentences
                sentences = re.split(r"(?<=[.!?])\s+", section)
                for sentence in sentences:
                    sentence_tokens = count_tokens(sentence)
                    if current_tokens + sentence_tokens > max_tokens:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                        current_tokens = sentence_tokens
                    else:
                        current_chunk += " " + sentence
                        current_tokens += sentence_tokens
            else:
                # Check if adding this section would exceed max
                if current_tokens + section_tokens > max_tokens:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = section
                    current_tokens = section_tokens
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + section
                    else:
                        current_chunk = section
                    current_tokens += section_tokens

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        # Validate chunk sizes
        validated_chunks = []
        for chunk in chunks:
            token_count = count_tokens(chunk)
            if min_tokens <= token_count <= max_tokens:
                validated_chunks.append(chunk)
            elif token_count < min_tokens:
                # Try to merge with next chunk
                continue
            # Skip chunks that are too large (already handled above)

        return validated_chunks

    def prepend_context(self, chunk_text: str, context_header: str) -> str:
        """Prepend section context to chunk."""
        if context_header:
            return f"## {context_header}\n\n{chunk_text}"
        return chunk_text

    def generate_chunk_id(self, source_url: str, page_index: int, chunk_index: int) -> str:
        """Generate unique chunk ID."""
        # Create deterministic hash
        hash_input = f"{source_url}_{page_index}_{chunk_index}"
        hash_obj = hashlib.md5(hash_input.encode())
        hash_hex = hash_obj.hexdigest()[:8]

        # Extract module/lesson from URL
        parts = source_url.split("/")
        module = ""
        lesson = ""

        for part in parts:
            if part.startswith("module-"):
                module = part.replace("module-", "mod")
            elif part.startswith("lesson-"):
                lesson = part.replace("lesson-", "less")

        return f"chunk_{hash_hex}_{module}_{lesson}_{chunk_index:03d}"

    def deduplicate_chunks(
        self, chunks: List[TextChunk], similarity_threshold: float = 0.95
    ) -> List[TextChunk]:
        """Deduplicate similar chunks."""
        deduplicated = []
        seen_hashes = set()

        for chunk in chunks:
            # Calculate hash for exact duplicates
            text_hash = hashlib.md5(chunk.text.encode()).hexdigest()

            if text_hash in seen_hashes:
                continue

            seen_hashes.add(text_hash)

            # Check for near-duplicates
            is_duplicate = False
            for existing in deduplicated:
                ratio = SequenceMatcher(None, chunk.text, existing.text).ratio()
                if ratio >= similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(chunk)

        return deduplicated

    def preprocess_crawled_content(self, crawl_results: List) -> List[TextChunk]:
        """Preprocess crawled content into chunks."""
        self.logger.log_info(f"Starting preprocessing of {len(crawl_results)} pages")

        all_chunks = []

        for page_idx, result in enumerate(crawl_results):
            # Normalize text
            text = self.normalize_text(result.text_content)
            text = self.remove_boilerplate(text)

            # Chunk text
            text_chunks = self.chunk_text(text)

            # Create TextChunk objects
            for chunk_idx, chunk_text in enumerate(text_chunks):
                # Prepend context
                chunk_with_context = self.prepend_context(chunk_text, result.section)

                # Generate ID
                chunk_id = self.generate_chunk_id(result.url, page_idx, chunk_idx)

                # Create metadata
                token_count = count_tokens(chunk_with_context)

                chunk_obj = TextChunk(
                    chunk_id=chunk_id,
                    source_url=result.url,
                    module=result.module,
                    section=result.section,
                    text=chunk_with_context,
                    token_count=token_count,
                    chunk_index=chunk_idx,
                    total_chunks=len(text_chunks),
                    created_at=datetime.utcnow(),
                )

                all_chunks.append(chunk_obj)

        # Deduplicate
        deduplicated = self.deduplicate_chunks(all_chunks)

        self.logger.log_operation(
            "preprocessing_complete",
            {
                "pages_processed": len(crawl_results),
                "chunks_created": len(all_chunks),
                "chunks_after_dedup": len(deduplicated),
            },
        )

        return deduplicated
