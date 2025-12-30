"""API routes for RAG Chatbot endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["RAG"])


# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for RAG query."""

    question: str = Field(..., min_length=3, max_length=1000, description="User question")
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")
    include_context: bool = Field(
        True, description="Whether to include formatted context in response"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Physical AI?",
                "top_k": 5,
                "include_context": True,
            }
        }


class SourceInfo(BaseModel):
    """Information about a source document."""

    url: str
    section: str
    score: float


class QueryResponse(BaseModel):
    """Response model for RAG query."""

    question: str
    context: Optional[str]
    sources: list[SourceInfo]
    metadata: dict


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    cohere: str
    qdrant: str
    model: str


# Global RAG service (will be initialized in app startup)
_rag_service: Optional[RAGService] = None


def set_rag_service(service: RAGService) -> None:
    """Set the RAG service instance."""
    global _rag_service
    _rag_service = service


def get_rag_service() -> RAGService:
    """Get the RAG service instance."""
    if _rag_service is None:
        raise RuntimeError("RAG service not initialized")
    return _rag_service


@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Query the RAG system",
    description="Submit a question to retrieve relevant documentation and context.",
)
async def query_rag(request: QueryRequest) -> QueryResponse:
    """
    Query the RAG system.

    Args:
        request: Query request with question and parameters

    Returns:
        QueryResponse with context and sources

    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Received query: {request.question}")

        service = get_rag_service()

        # Process query through RAG pipeline
        result = service.query(
            question=request.question,
            top_k=request.top_k,
            include_context=request.include_context,
        )

        # Convert response to model
        response = QueryResponse(
            question=result["question"],
            context=result["context"],
            sources=[SourceInfo(**s) for s in result["sources"]],
            metadata=result["metadata"],
        )

        logger.info(f"Query processed successfully")
        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health of the RAG service.",
)
async def health_check() -> HealthResponse:
    """
    Check health of RAG service.

    Returns:
        HealthResponse with service status

    Raises:
        HTTPException: If service is unhealthy
    """
    try:
        logger.debug("Health check requested")

        service = get_rag_service()
        health = service.health_check()

        if health.get("status") == "unhealthy":
            raise HTTPException(status_code=503, detail="Service unhealthy")

        return HealthResponse(
            status=health.get("status", "unknown"),
            cohere=health.get("cohere", "unknown"),
            qdrant=health.get("qdrant", "unknown"),
            model=health.get("model", "unknown"),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/info", summary="Service information", description="Get service information.")
async def service_info() -> dict:
    """
    Get service information.

    Returns:
        Dictionary with service info
    """
    try:
        service = get_rag_service()
        qdrant_info = service.qdrant_service.get_collection_info()

        return {
            "name": "RAG Chatbot API",
            "version": "1.0.0",
            "model": service.model,
            "collection": qdrant_info,
        }

    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service info")
