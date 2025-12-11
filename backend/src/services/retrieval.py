"""
Qdrant Vector Database Retrieval Service
Handles document embedding and retrieval from Qdrant
"""

import logging
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import cohere
from uuid import uuid4
import time

from src.config.settings import settings
from src.models import ContextChunk

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving documents from Qdrant vector database"""

    def __init__(self):
        """Initialize Qdrant client and Cohere embeddings"""
        try:
            # Initialize Qdrant client
            self.qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=settings.api_timeout
            )

            # Initialize Cohere client for embeddings
            self.cohere_client = cohere.ClientV2(api_key=settings.cohere_api_key)

            self.collection_name = settings.qdrant_collection_name
            self.embedding_dim = settings.embedding_dimension
            self.embedding_model = settings.embedding_model

            logger.info(f"✅ Retrieval service initialized with Qdrant")

        except Exception as e:
            logger.error(f"❌ Failed to initialize retrieval service: {e}")
            raise

    def get_or_create_collection(self):
        """Get existing collection or create new one if not exists"""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Collection created: {self.collection_name}")
            else:
                logger.info(f"✅ Using existing collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"❌ Failed to get/create collection: {e}")
            raise

    def embed_text(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using Cohere

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            # Use Cohere API to generate embeddings
            response = self.cohere_client.embed(
                texts=texts,
                model=self.embedding_model,
                input_type="search_document"
            )

            embeddings = response.embeddings
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"❌ Failed to embed texts: {e}")
            raise

    def add_documents(
        self,
        documents: List[dict],
        batch_size: int = 100
    ) -> int:
        """
        Add documents to Qdrant collection

        Args:
            documents: List of documents with 'text', 'source_url', 'title' fields
            batch_size: Number of documents to process in each batch

        Returns:
            Number of documents added
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return 0

            self.get_or_create_collection()

            total_added = 0

            # Process documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                texts = [doc.get("text", "") for doc in batch]

                # Generate embeddings
                embeddings = self.embed_text(texts)

                # Prepare points for Qdrant
                points = []
                for j, (doc, embedding) in enumerate(zip(batch, embeddings)):
                    point_id = int(uuid4().int % 2**63)  # Convert UUID to positive int

                    point = PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "text": doc.get("text", ""),
                            "source_url": doc.get("source_url", ""),
                            "title": doc.get("title", ""),
                            "chapter": doc.get("chapter", ""),
                            "metadata": doc.get("metadata", {})
                        }
                    )
                    points.append(point)

                # Upload to Qdrant
                self.qdrant_client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )

                total_added += len(points)
                logger.info(f"✅ Added batch {i//batch_size + 1}: {len(points)} documents")

            return total_added

        except Exception as e:
            logger.error(f"❌ Failed to add documents: {e}")
            raise

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3
    ) -> List[ContextChunk]:
        """
        Retrieve relevant documents from Qdrant

        Args:
            query: The user's query
            top_k: Number of top results to retrieve
            score_threshold: Minimum relevance score (0-1)

        Returns:
            List of ContextChunk objects
        """
        try:
            # Check if collection exists
            try:
                self.qdrant_client.get_collection(self.collection_name)
            except Exception:
                logger.warning(f"Collection '{self.collection_name}' does not exist or is empty")
                return []

            # Embed the query
            query_embedding = self.embed_text([query])[0]

            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold
            )

            # Convert results to ContextChunk objects
            context_chunks = []
            for result in search_results:
                payload = result.payload

                # Ensure relevance_score is between 0 and 1
                relevance_score = max(0.0, min(1.0, result.score))

                chunk = ContextChunk(
                    source_url=payload.get("source_url", ""),
                    relevance_score=relevance_score,
                    text=payload.get("text", "")[:500],  # Limit to 500 chars
                    metadata={
                        "title": payload.get("title", ""),
                        "chapter": payload.get("chapter", ""),
                        **payload.get("metadata", {})
                    }
                )
                context_chunks.append(chunk)

            logger.info(f"✅ Retrieved {len(context_chunks)} context chunks")
            return context_chunks

        except Exception as e:
            logger.error(f"❌ Failed to retrieve context: {e}")
            return []

    def health_check(self) -> bool:
        """Check if Qdrant is accessible"""
        try:
            self.qdrant_client.get_collections()
            return True
        except Exception as e:
            logger.error(f"❌ Qdrant health check failed: {e}")
            return False


# Global retrieval service instance
_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    """Get or create the retrieval service"""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
