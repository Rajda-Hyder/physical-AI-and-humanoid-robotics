"""
Request models for the RAG Chatbot API
"""

from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """User query request to the RAG chatbot"""

    query: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's question or query",
        example="What is physical AI?"
    )

    context: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional selected text from documentation for context",
        example="Selected text from the page..."
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for multi-turn interactions",
        example="uuid-here"
    )

    stream: bool = Field(
        default=False,
        description="Whether to stream the response (Server-Sent Events)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is physical AI?",
                "context": None,
                "stream": False
            }
        }
