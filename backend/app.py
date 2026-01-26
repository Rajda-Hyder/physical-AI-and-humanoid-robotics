"""FastAPI application for RAG Chatbot API."""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import router
from backend.services import QdrantService, RAGService
from backend.api.routes import set_rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Global service instance
_rag_service: RAGService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.

    Startup:
    - Initialize RAG service with Qdrant and Cohere
    - Perform health checks

    Shutdown:
    - Clean up resources
    """
    try:
        # Startup
        logger.info("Starting RAG Chatbot API...")

        # Load configuration from environment
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        qdrant_collection = os.getenv("QDRANT_COLLECTION_NAME", "documents")
        cohere_api_key = os.getenv("COHERE_API_KEY")

        # Validate required environment variables
        if not qdrant_url:
            raise ValueError("QDRANT_URL environment variable is required")
        if not qdrant_api_key:
            raise ValueError("QDRANT_API_KEY environment variable is required")
        if not cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable is required")

        logger.info(f"Connecting to Qdrant: {qdrant_url}")
        logger.info(f"Collection: {qdrant_collection}")

        # Initialize services
        qdrant_service = QdrantService(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name=qdrant_collection,
        )

        rag_service = RAGService(
            cohere_api_key=cohere_api_key,
            qdrant_service=qdrant_service,
            model="embed-english-v3.0",
        )

        # Set global service
        set_rag_service(rag_service)
        global _rag_service
        _rag_service = rag_service

        # Health check
        logger.info("Performing health check...")
        health = rag_service.health_check()
        logger.info(f"Health check result: {health}")

        if health.get("status") == "unhealthy":
            raise RuntimeError("Service health check failed")

        logger.info("RAG Chatbot API started successfully")

        yield

        # Shutdown
        logger.info("Shutting down RAG Chatbot API...")

    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        raise


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation API using Cohere and Qdrant",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://physical-ai-and-humanoid-robotics-eight.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
