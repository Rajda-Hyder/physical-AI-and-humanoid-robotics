"""Qdrant vector database service for RAG backend."""

import logging
from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self, url: str, api_key: str, collection_name: str = "documents"):
        """
        Initialize Qdrant service.

        Args:
            url: Qdrant server URL
            api_key: Qdrant API key
            collection_name: Name of the collection to use
        """
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name

        try:
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                prefer_grpc=False,
            )
            logger.info(f"Connected to Qdrant at {url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar vectors in the collection.

        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return

        Returns:
            List of search results with metadata
        """
        try:
            logger.debug(f"Searching for top {top_k} similar vectors")

            query_vector = [float(x) for x in query_vector]


            results = self.client.search_points(
                collection_name=self.collection_name,
                vector=query_vector,
                limit=top_k,
                with_payload=True,
            )

            search_results = []
            for result in results.points:
                if result.payload is None:
                    continue

                search_results.append(
                    {
                        "chunk_id": result.payload.get("chunk_id", ""),
                        "score": float(result.score),
                        "text": result.payload.get("text", ""),
                        "source_url": result.payload.get("source_url", ""),
                        "module": result.payload.get("module", ""),
                        "section": result.payload.get("section", ""),
                    }
                )

            logger.info(f"Found {len(search_results)} results for query")
            return search_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def get_collection_info(self) -> Dict:
        """
        Get collection information.

        Returns:
            Dictionary with collection metadata
        """
        try:
            info = self.client.get_collection(collection_name=self.collection_name)

            # Handle different Qdrant SDK versions
            points_count = getattr(info, "points_count", 0)
            vectors_count = getattr(info, "vectors_count", None)

            return {
                "name": self.collection_name,
                "points_count": points_count,
                "vectors_count": vectors_count,
            }

        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise

    def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            self.client.get_collection(collection_name=self.collection_name)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
