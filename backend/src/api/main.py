"""
FastAPI entry point for RAG Chatbot API
"""

import os
from dotenv import load_dotenv

# 1️⃣ Load environment FIRST
load_dotenv(override=True)

# 2️⃣ Hard-fail if critical secrets are missing
assert os.getenv("COHERE_API_KEY"), "COHERE_API_KEY is missing at runtime"
assert os.getenv("QDRANT_URL"), "QDRANT_URL is missing at runtime"
assert os.getenv("QDRANT_COLLECTION_NAME"), "QDRANT_COLLECTION_NAME is missing at runtime"

# 3️⃣ Import FastAPI and router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
from src.services import QdrantService, RAGService
from routes import set_rag_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 4️⃣ Create app
app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# 5️⃣ Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6️⃣ Lifespan: initialize RAG service
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting RAG Chatbot API...")

        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        qdrant_collection = os.getenv("QDRANT_COLLECTION_NAME")
        cohere_api_key = os.getenv("COHERE_API_KEY")

        # Initialize services
        qdrant_service = QdrantService(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name=qdrant_collection,
        )

        rag_service = RAGService(
            cohere_api_key=cohere_api_key,
            qdrant_service=qdrant_service,
        )

        # Set global service
        set_rag_service(rag_service)

        # Health check
        health = rag_service.health_check()
        logger.info(f"Health check: {health}")

        if health.get("status") != "healthy":
            raise RuntimeError("Service health check failed")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

# 7️⃣ Register routes
app.include_router(router)

# 8️⃣ Root endpoint
@app.get("/")
async def root():
    return {
        "name": "RAG Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }

