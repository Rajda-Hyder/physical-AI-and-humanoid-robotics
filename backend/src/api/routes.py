"""
API Routes for RAG Chatbot
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

from src.models import QueryRequest, ResponsePayload, ErrorResponse
from src.services import get_rag_agent, get_retrieval_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    try:
        retrieval_service = get_retrieval_service()
        is_healthy = retrieval_service.health_check()

        if is_healthy:
            return {
                "status": "healthy",
                "version": "1.0.0",
                "service": "RAG Chatbot API"
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Qdrant connection failed"
            }, 503

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": str(e)
        }, 503


@router.post("/query", response_model=ResponsePayload, tags=["chat"])
async def submit_query(request: QueryRequest):
    """
    Submit a query to the RAG chatbot

    Accepts a user query and optional context, returns an AI-generated response
    grounded in the knowledge base with source attribution.
    """
    try:
        logger.info(f"📨 Received query: {request.query[:100]}...")

        # Validate query
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Query cannot be empty"
                    }
                }
            )

        # Process the query
        rag_agent = get_rag_agent()
        response = rag_agent.process_query(
            query=request.query,
            context=request.context,
            conversation_id=request.conversation_id
        )

        logger.info(f"✅ Query processed successfully: {response.response_id}")
        return response

    except HTTPException:
        raise

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )

    except TimeoutError:
        logger.error("Request timeout")
        raise HTTPException(
            status_code=504,
            detail={
                "error": {
                    "code": "TIMEOUT",
                    "message": "Request exceeded timeout limit"
                }
            }
        )

    except Exception as e:
        logger.error(f"❌ Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An error occurred while processing your query"
                }
            }
        )


@router.post("/query/stream", tags=["chat"])
async def submit_query_stream(request: QueryRequest):
    """
    Submit a query with streaming response (Server-Sent Events)

    Returns answer chunks as they are generated.
    """
    try:
        logger.info(f"📨 Received streaming query: {request.query[:100]}...")

        # Validate query
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Query cannot be empty"
                    }
                }
            )

        # Process the query
        rag_agent = get_rag_agent()
        response = rag_agent.process_query(
            query=request.query,
            context=request.context,
            conversation_id=request.conversation_id
        )

        logger.info(f"✅ Streaming query processed: {response.response_id}")
        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"❌ Error processing streaming query: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "An error occurred while processing your query"
                }
            }
        )


@router.get("/info", tags=["info"])
async def get_api_info():
    """Get API information and configuration"""
    try:
        retrieval_service = get_retrieval_service()
        collections = retrieval_service.qdrant_client.get_collections()
        collection_count = len(collections.collections) if collections else 0

        return {
            "name": "RAG Chatbot API",
            "version": "1.0.0",
            "description": "Retrieval-Augmented Generation chatbot for Physical AI textbook",
            "endpoints": {
                "health": "/api/v1/health",
                "query": "/api/v1/query",
                "query_stream": "/api/v1/query/stream",
                "info": "/api/v1/info"
            },
            "integrations": {
                "qdrant_collection_count": collection_count,
                "embedding_model": "cohere",
                "response_model": "cohere-command-r-plus"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get API info: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SERVER_ERROR",
                    "message": "Failed to retrieve API information"
                }
            }
        )
