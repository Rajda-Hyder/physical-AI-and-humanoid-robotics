"""
FastAPI routes for RAG Chatbot
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from src.models import QueryRequest, ResponsePayload, SourceReference, ResponseMetadata
from src.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["RAG"])

# Global RAG service
_rag_service: Optional[RAGService] = None

def set_rag_service(service: RAGService) -> None:
    global _rag_service
    _rag_service = service

def get_rag_service() -> RAGService:
    if _rag_service is None:
        raise RuntimeError("RAG service not initialized")
    return _rag_service

# -------------------------------
# Query endpoint
# -------------------------------
@router.post("/query", response_model=ResponsePayload, summary="Query the RAG system")
async def query_rag(request: QueryRequest) -> ResponsePayload:
    try:
        service = get_rag_service()
        question = request.get_question()
        result = service.query(
            question=question,
            context=request.context,
            conversation_id=request.conversation_id,
            top_k=request.top_k,
            include_context=request.include_context,
            include_sources=request.include_sources,
        )

        # Prepare sources
        sources: List[SourceReference] = []
        if request.include_sources:
            for s in result.get("sources", []):
                sources.append(SourceReference(
                    url=s.get("url"),
                    section=s.get("section"),
                    score=s.get("score"),
                ))

        # Build metadata
        metadata = ResponseMetadata(
            model=result["metadata"].get("model", "unknown"),
            context_chunks=result["metadata"].get("context_chunks", 0),
            query_succeeded=result["metadata"].get("query_succeeded", False)
        )

        # Build response
        response = ResponsePayload(
            question=question,
            answer=result.get("answer", "No relevant answer found."),
            context=result.get("context") if request.include_context else None,
            sources=sources if request.include_sources else None,
            metadata=metadata
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Query processing failed")

# -------------------------------
# Health endpoint
# -------------------------------
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str
    cohere: str
    qdrant: str
    model: str

@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    try:
        service = get_rag_service()
        health = service.health_check()
        return HealthResponse(
            status=health.get("status", "unknown"),
            cohere=health.get("cohere", "unknown"),
            qdrant=health.get("qdrant", "unknown"),
            model=health.get("model", "unknown"),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# -------------------------------
# Info endpoint
# -------------------------------
@router.get("/info", summary="Service information")
async def service_info():
    try:
        service = get_rag_service()
        collection_info = service.qdrant_service.get_collection_info()
        return {
            "name": "RAG Chatbot API",
            "version": "1.0.0",
            "model": service.model,
            "collection": collection_info,
        }
    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service info")
