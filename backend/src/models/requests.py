"""
Request models for the RAG Chatbot API

This file defines all incoming request schemas
used by the FastAPI routes.
"""

from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """
    Unified request model for RAG queries.

    Supports both:
    - `query`  (frontend standard)
    - `question` (backend/internal standard)
    """

    # Frontend usually sends this
    query: Optional[str] = Field(
        default=None,
        description="User query from frontend",
        example="What is Physical AI?"
    )

    # Backend / internal naming
    question: Optional[str] = Field(
        default=None,
        description="User question",
        example="Explain Physical AI in simple terms"
    )

    context: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Optional selected documentation text used as extra context",
        example="Physical AI refers to systems that interact with the real world..."
    )

    conversation_id: Optional[str] = Field(
        default=None,
        description="Conversation identifier for multi-turn chat",
        example="b1a2c3d4-uuid"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant context chunks to retrieve"
    )

    include_context: bool = Field(
        default=True,
        description="Whether to include retrieved context in API response"
    )

    include_sources: bool = Field(
        default=False,
        description="Whether to include source URLs in response"
    )

    stream: bool = Field(
        default=False,
        description="Enable streaming response (future use)"
    )

    def get_question(self) -> str:
        """
        Returns the final validated user question.

        Priority:
        1. question
        2. query

        Raises error if both are missing.
        """

        if self.question and self.question.strip():
            return self.question.strip()

        if self.query and self.query.strip():
            return self.query.strip()

        raise ValueError("Either 'query' or 'question' must be provided.")
