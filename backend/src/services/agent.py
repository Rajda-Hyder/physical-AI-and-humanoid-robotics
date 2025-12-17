"""
RAG Agent Service
Generates grounded responses using retrieved context
"""

import logging
import time
from typing import Optional
import cohere

from src.config.settings import settings
from src.models import ContextChunk, ResponsePayload, ResponseMetadata
from .retrieval import get_retrieval_service

logger = logging.getLogger(__name__)


class RAGAgent:
    """Agent for generating context-grounded responses"""

    def __init__(self):
        """Initialize the RAG agent with Cohere client"""
        try:
            self.cohere_client = cohere.ClientV2(api_key=settings.cohere_api_key)
            logger.info("✅ RAG Agent initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG Agent: {e}")
            raise

    def generate_response(
        self,
        query: str,
        context_chunks: list[ContextChunk],
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Generate a response grounded in the context

        Args:
            query: The user's query
            context_chunks: Retrieved context documents
            conversation_history: Optional conversation history for multi-turn

        Returns:
            Generated response string
        """
        try:
            # Build context string from chunks
            context_str = self._build_context(context_chunks)

            # Build the prompt with instructions
            system_prompt = """You are a helpful AI assistant for a Physical AI and Humanoid Robotics textbook.
Your role is to answer questions about the textbook content based on the provided context.

IMPORTANT RULES:
1. Base your answers ONLY on the provided context
2. If the context doesn't contain relevant information, clearly say so
3. Cite the sources when using specific information
4. Be concise but thorough
5. Use markdown formatting for readability
6. If asked about something outside the scope, politely redirect to the textbook content"""

            user_message = f"""Question: {query}

{context_str}

Please answer the question based on the context provided above. If the context is empty or not relevant, explain what information you would need."""

            # Call Cohere API to generate response
            response = self.cohere_client.chat(
                model="command-r",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            answer = response.message.content[0].text

            logger.info(f"✅ Generated response ({len(answer)} chars)")
            return answer

        except Exception as e:
            logger.error(f"❌ Failed to generate response: {e}")
            raise

    def _build_context(self, context_chunks: list[ContextChunk]) -> str:
        """Build context string from chunks"""
        if not context_chunks:
            return "No relevant context found in the knowledge base."

        context_parts = ["RELEVANT CONTEXT FROM TEXTBOOK:\n"]

        for i, chunk in enumerate(context_chunks, 1):
            # Format source information
            source = chunk.source_url or "Unknown source"
            score = f"{chunk.relevance_score:.1%}" if chunk.relevance_score else "unknown"

            context_parts.append(f"\n[Source {i}]: {source} (Relevance: {score})")
            context_parts.append(f"Content: {chunk.text}")

        return "\n".join(context_parts)

    def process_query(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> ResponsePayload:
        """
        Process a user query end-to-end

        Args:
            query: The user's query
            context: Optional selected text context
            conversation_id: Optional conversation ID

        Returns:
            ResponsePayload with generated response
        """
        start_time = time.time()
        import uuid

        try:
            # Retrieve context from Qdrant
            retrieval_service = get_retrieval_service()

            # Combine query with context if provided
            search_query = query
            if context:
                search_query = f"{query}\n\nContext: {context}"

            context_chunks = retrieval_service.retrieve_context(
                query=search_query,
                top_k=5,
                score_threshold=0.3
            )

            logger.info(f"Retrieved {len(context_chunks)} context chunks")

            # Generate response with context
            answer = self.generate_response(
                query=query,
                context_chunks=context_chunks,
                conversation_history=None
            )

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Create response payload
            response = ResponsePayload(
                response_id=str(uuid.uuid4()),
                answer=answer,
                context_chunks=context_chunks,
                metadata=ResponseMetadata(
                    model="cohere-command-r",
                    tokens_used=len(query.split()) + len(answer.split()),  # Rough estimate
                    response_time_ms=response_time_ms,
                    timestamp=int(time.time() * 1000),
                    version="1.0.0"
                )
            )

            logger.info(f"✅ Query processed in {response_time_ms}ms")
            return response

        except Exception as e:
            logger.error(f"❌ Failed to process query: {e}")
            raise


# Global agent instance
_rag_agent: Optional[RAGAgent] = None


def get_rag_agent() -> RAGAgent:
    """Get or create the RAG agent"""
    global _rag_agent
    if _rag_agent is None:
        _rag_agent = RAGAgent()
    return _rag_agent
