"""Qdrant vector database integration."""

from typing import Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models

from .logging_utils import get_logger


class QdrantVectorStore:
    """Manages vector storage in Qdrant Cloud."""

    def __init__(self, url: str, api_key: str, collection_name: str = "documents"):
        """Initialize Qdrant vector store."""
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.logger = get_logger()

        try:
            self.client = QdrantClient(url=url, api_key=api_key)
            self.logger.log_info(f"Connected to Qdrant at {url}")
        except Exception as e:
            self.logger.log_error(f"Failed to connect to Qdrant: {e}")
            raise

    def create_collection(self, vector_size: int = 1024) -> bool:
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                self.logger.log_info(f"Collection '{self.collection_name}' already exists")
                return False

            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )

            self.logger.log_info(f"Created collection '{self.collection_name}' with size {vector_size}")
            return True

        except Exception as e:
            self.logger.log_error(f"Failed to create collection: {e}")
            raise

    def store_embeddings(self, embeddings: List[List[float]], chunks: List) -> int:
        """Store embeddings with metadata in Qdrant."""
        try:
            points = []

            for idx, (embedding, chunk) in enumerate(zip(embeddings, chunks)):
                # Create point with metadata
                point = models.PointStruct(
                    id=idx,
                    vector=embedding,
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "source_url": chunk.source_url,
                        "module": chunk.module,
                        "section": chunk.section,
                        "text": chunk.text,
                        "token_count": chunk.token_count,
                        "created_at": chunk.created_at.isoformat(),
                    },
                )
                points.append(point)

            # Upload points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            self.logger.log_operation(
                "vectors_stored",
                {"count": len(points), "collection": self.collection_name},
            )

            return len(points)

        except Exception as e:
            self.logger.log_error(f"Failed to store embeddings: {e}")
            raise

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar vectors."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )

            search_results = []
            for result in results:
                search_results.append(
                    {
                        "chunk_id": result.payload.get("chunk_id"),
                        "score": result.score,
                        "text": result.payload.get("text"),
                        "source_url": result.payload.get("source_url"),
                        "module": result.payload.get("module"),
                    }
                )

            return search_results

        except Exception as e:
            self.logger.log_error(f"Search failed: {e}")
            raise

    def get_collection_info(self) -> Dict:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
            }
        except Exception as e:
            self.logger.log_error(f"Failed to get collection info: {e}")
            raise
