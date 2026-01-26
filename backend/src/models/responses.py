"""
Response models for the RAG Chatbot API

Defines all structured API responses returned
to the frontend.
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ContextChunk(BaseModel):
    """
    Individual retrieved context chunk
    """

    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SourceReference(BaseModel):
    """
    Source reference from documentation
    """

    url: Optional[str] = None
    section: Optional[str] = None
    score: Optional[float] = None


class ResponseMetadata(BaseModel):
    """
    Metadata about the RAG execution
    """

    model: str
    context_chunks: int
    query_succeeded: bool


class ResponsePayload(BaseModel):
    """
    Main successful response payload
    """

    question: str
    answer: str

    context: Optional[str] = None

    sources: Optional[List[SourceReference]] = None

    metadata: ResponseMetadata


class ErrorResponse(BaseModel):
    """
    Standard error response
    """

    detail: str
