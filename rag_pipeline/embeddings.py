"""Embedding generation using Cohere API."""

from typing import Dict, List

import cohere

from .logging_utils import get_logger
from .utils.retry import ExponentialBackoff
import time

class CohereEmbeddingsGenerator:
    """Generates embeddings using Cohere API."""

    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        """Initialize Cohere embeddings generator."""
        self.api_key = api_key
        self.model = model
        self.client = cohere.ClientV2(api_key=api_key)
        self.logger = get_logger()
        self.embedding_dimension = 1024  # For embed-english-v3.0

    def generate_embeddings(
        self, texts: List[str], batch_size: int = 20, max_retries: int = 5
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        all_embeddings = []
        backoff = ExponentialBackoff(max_attempts=max_retries)

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            self.logger.log_info(
                f"Generating embeddings for batch {i // batch_size + 1} "
                f"({len(batch)} texts)"
            )

            retries = 0
            while retries < max_retries:
                try:
                    response = self.client.embed(
                        texts=batch,
                        model=self.model,
                        input_type="search_document",
                    )

                    embeddings = list(response.embeddings.float)
                    all_embeddings.extend(embeddings)

                    self.logger.log_operation(
                        "embedding_batch_complete",
                        {"batch_size": len(batch), "embedding_dimension": len(embeddings[0])},
                    )
                    break

                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        self.logger.log_error(f"Failed to generate embeddings after {max_retries} retries: {e}")
                        raise
                    backoff.wait()
            time.sleep(12)


        return all_embeddings

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.embedding_dimension


def generate_and_store_embeddings(chunks: List, config: Dict, vector_store) -> Dict:
    """Generate embeddings for chunks and store in vector database."""
    logger = get_logger()
    embedding_config = config

    logger.log_operation("embedding_pipeline_start", {"chunk_count": len(chunks)})

    # Initialize embeddings generator
    generator = CohereEmbeddingsGenerator(
        api_key=embedding_config.get("api_key"),
        model=embedding_config.get("model", "embed-english-v3.0"),
    )

    # Extract texts for embedding
    texts = [chunk.text for chunk in chunks]

    # Generate embeddings
    try:
        embeddings = generator.generate_embeddings(
            texts,
            batch_size=embedding_config.get("batch_size", 20),
            max_retries=embedding_config.get("retry_max_attempts", 5),
        )
    except Exception as e:
        logger.log_error(f"Embedding generation failed: {e}")
        raise

    # Store embeddings
    try:
        stored_count = vector_store.store_embeddings(embeddings, chunks)
        logger.log_operation(
            "embedding_pipeline_complete",
            {
                "total_embeddings": len(embeddings),
                "stored_count": stored_count,
                "dimension": generator.get_embedding_dimension(),
            },
        )
        return {
            "success": True,
            "embeddings_generated": len(embeddings),
            "embeddings_stored": stored_count,
            "dimension": generator.get_embedding_dimension(),
        }
    except Exception as e:
        logger.log_error(f"Storing embeddings failed: {e}")
        raise
