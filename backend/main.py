"""
RAG Chatbot Backend - Main Application
FastAPI server for Retrieval-Augmented Generation chatbot
"""

import logging
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import settings
from src.api.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting RAG Chatbot API...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Qdrant URL: {settings.qdrant_url}")
    logger.info(f"Collection: {settings.qdrant_collection_name}")

    yield

    # Shutdown
    logger.info("🛑 Shutting down RAG Chatbot API...")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for Physical AI textbook",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - Allow requests from Docusaurus frontend
cors_origins = [
    "http://localhost:3000",        # Local development
    "http://localhost:8000",        # Local development (same port)
    "http://127.0.0.1:3000",        # Local loopback
    "http://127.0.0.1:8000",        # Local loopback
]

# Add production domains if configured
if not settings.debug:
    # For production, add your actual domain
    cors_origins.extend([
        # "https://yourdomain.com",
        # "https://www.yourdomain.com",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi_schema": "/openapi.json"
    }


@app.get("/docs", tags=["docs"], include_in_schema=False)
async def docs():
    """Redirect to Swagger UI"""
    return {"message": "API documentation available at /docs (Swagger UI)"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting RAG Chatbot Backend Server...")
    logger.info(f"Host: {settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
