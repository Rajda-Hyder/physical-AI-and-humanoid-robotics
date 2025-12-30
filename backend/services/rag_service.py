"""RAG (Retrieval-Augmented Generation) service."""

import logging
from typing import Dict, List, Optional

import cohere

from .qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieval-augmented generation using Cohere and Qdrant."""

    def __init__(
        self,
        cohere_api_key: str,
        qdrant_service: QdrantService,
        model: str = "embed-english-v3.0",
    ):
        """
        Initialize RAG service.

        Args:
            cohere_api_key: Cohere API key
            qdrant_service: Initialized Qdrant service
            model: Cohere embedding model to use
        """
        self.model = model
        self.qdrant_service = qdrant_service
        self.embedding_dimension = 1024

        try:
            self.cohere_client = cohere.Client(api_key=cohere_api_key)
            logger.info("Cohere client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cohere client: {e}")
            raise

    def _embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using Cohere.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.cohere_client.embed(
                texts=[text],
                model=self.model,
                input_type="search_query",
            )
            embedding = list(response.embeddings.float[0])
            logger.debug(f"Generated embedding for query (dim: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def _retrieve_context(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context from vector database.

        Args:
            query_vector: Query embedding
            top_k: Number of results to retrieve

        Returns:
            List of relevant documents/chunks
        """
        try:
            results = self.qdrant_service.search(query_vector, top_k=top_k)
            logger.info(f"Retrieved {len(results)} context chunks")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            raise

    def _format_context(self, context: List[Dict]) -> str:
        """
        Format retrieved context into a readable string.

        Args:
            context: List of context chunks

        Returns:
            Formatted context string
        """
        if not context:
            return "No relevant context found."

        formatted = "## Context from Documentation\n\n"
        for i, chunk in enumerate(context, 1):
            source = chunk.get("source_url", "Unknown source")
            section = chunk.get("section", "No section")
            score = chunk.get("score", 0)
            text = chunk.get("text", "")

            # Limit text preview
            text_preview = text[:300] + "..." if len(text) > 300 else text

            formatted += f"**Source {i}** (Score: {score:.3f})\n"
            formatted += f"- URL: {source}\n"
            formatted += f"- Section: {section}\n"
            formatted += f"- Content: {text_preview}\n\n"

        return formatted

    def query(
        self,
        question: str,
        top_k: int = 5,
        include_context: bool = True,
    ) -> Dict:
        """
        Process a question using RAG.

        Args:
            question: User question
            top_k: Number of context chunks to retrieve
            include_context: Whether to include context in response

        Returns:
            Dictionary with question, context, and metadata
        """
        try:
            logger.info(f"Processing question: {question}")

            # Validate input
            if not question or not isinstance(question, str):
                raise ValueError("Question must be a non-empty string")

            if len(question.strip()) < 3:
                raise ValueError("Question is too short (minimum 3 characters)")

            # Step 1: Embed the question
            logger.debug("Step 1: Embedding question")
            query_vector = self._embed_text(question)

            # Step 2: Retrieve context
            logger.debug("Step 2: Retrieving context from Qdrant")
            context = self._retrieve_context(query_vector, top_k=top_k)

            # Step 3: Format context
            logger.debug("Step 3: Formatting context")
            formatted_context = self._format_context(context)

            # Step 4: Build response
            logger.debug("Step 4: Building response")
            response = {
                "question": question,
                "context": formatted_context if include_context else None,
                "sources": [
                    {
                        "url": c.get("source_url"),
                        "section": c.get("section"),
                        "score": c.get("score"),
                    }
                    for c in context
                ],
                "metadata": {
                    "model": self.model,
                    "context_chunks": len(context),
                    "query_succeeded": True,
                },
            }

            logger.info(f"Query processed successfully, returned {len(context)} sources")
            return response

        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            raise

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise

    def health_check(self) -> Dict:
        """
        Check health of RAG service.

        Returns:
            Health status dictionary
        """
        try:
            qdrant_healthy = self.qdrant_service.health_check()

            return {
                "status": "healthy" if qdrant_healthy else "degraded",
                "cohere": "connected",
                "qdrant": "connected" if qdrant_healthy else "disconnected",
                "model": self.model,
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }
