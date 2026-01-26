"""Services package"""

from .rag_service import RAGService
from .qdrant_service import QdrantService
from src.config import settings

from .retrieval import RetrievalService, get_retrieval_service
from .agent import RAGAgent, get_rag_agent

__all__ = [
    "RetrievalService",
    "get_retrieval_service",
    "RAGAgent",
    "get_rag_agent",
    "RAGService",
    "QdrantService",
    "get_real_rag_service",
]

_rag_service_instance = None


def get_real_rag_service():
    global _rag_service_instance

    if _rag_service_instance is None:
        qdrant = QdrantService(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

        _rag_service_instance = RAGService(
            cohere_api_key=settings.cohere_api_key,
            qdrant_service=qdrant,
        )

    return _rag_service_instance
