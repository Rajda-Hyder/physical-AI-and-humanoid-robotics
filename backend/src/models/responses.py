"""
Response models for the RAG Chatbot API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ContextChunk(BaseModel):
    """A retrieved source document"""

    source_url: str = Field(
        ...,
        description="URL to the source documentation",
        example="/docs/chapter-1/intro#physical-ai"
    )

    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score (0-1, higher = more relevant)",
        example=0.95
    )

    text: str = Field(
        ...,
        max_length=500,
        description="Text preview/excerpt from the source",
        example="Physical AI refers to..."
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the source",
        example={"title": "Introduction to Physical AI", "chapter": "Chapter 1"}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "source_url": "/docs/chapter-1/intro#physical-ai",
                "relevance_score": 0.95,
                "text": "Physical AI refers to...",
                "metadata": {"title": "Introduction"}
            }
        }


class ResponseMetadata(BaseModel):
    """Metadata about the response"""

    model: str = Field(
        ...,
        description="AI model used for generation",
        example="cohere"
    )

    tokens_used: int = Field(
        ...,
        ge=0,
        description="Total tokens used"
    )

    response_time_ms: int = Field(
        ...,
        ge=0,
        description="Time taken to generate response (milliseconds)"
    )

    timestamp: int = Field(
        ...,
        description="Server timestamp of response (Unix milliseconds)"
    )

    version: str = Field(
        default="1.0.0",
        description="API version"
    )


class ResponsePayload(BaseModel):
    """Complete response from the RAG backend"""

    response_id: str = Field(
        ...,
        description="Unique identifier for this response",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    answer: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="AI-generated response (markdown formatted)"
    )

    context_chunks: List[ContextChunk] = Field(
        default_factory=list,
        max_length=10,
        description="Retrieved source documents ranked by relevance"
    )

    metadata: ResponseMetadata = Field(
        ...,
        description="Response metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response_id": "uuid-here",
                "answer": "Physical AI refers to...",
                "context_chunks": [
                    {
                        "source_url": "/docs/chapter-1",
                        "relevance_score": 0.95,
                        "text": "..."
                    }
                ],
                "metadata": {
                    "model": "cohere",
                    "tokens_used": 156,
                    "response_time_ms": 2341,
                    "timestamp": 1702329603000,
                    "version": "1.0.0"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""

    error: Dict[str, Any] = Field(
        ...,
        description="Error details",
        example={
            "code": "TIMEOUT",
            "message": "Request exceeded 30 second timeout"
        }
    )
