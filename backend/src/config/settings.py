"""
Configuration management for RAG Chatbot Backend
Loads environment variables from .env file
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Qdrant Configuration
    qdrant_api_key: str = Field(..., alias="QDRANT_API_KEY")
    qdrant_url: str = Field(..., alias="QDRANT_URL")
    qdrant_collection_name: str = Field(default="documents", alias="QDRANT_COLLECTION_NAME")

    # Cohere Configuration
    cohere_api_key: str = Field(..., alias="COHERE_API_KEY")
    cohere_model: str = Field(default="command-r-plus-08-2024", alias="COHERE_MODEL")
    embedding_model: str = Field(default="embed-english-v3.0", alias="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=1024, alias="EMBEDDING_DIMENSION")

    # OpenAI Configuration (optional)
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # FastAPI Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_timeout: int = Field(default=30, alias="API_TIMEOUT")

    # Application Settings
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)
        # Validate required API keys
        errors = []
        if not self.qdrant_api_key or self.qdrant_api_key.isspace():
            errors.append("QDRANT_API_KEY environment variable is required and cannot be empty")
        if not self.qdrant_url or self.qdrant_url.isspace():
            errors.append("QDRANT_URL environment variable is required and cannot be empty")
        if not self.cohere_api_key or self.cohere_api_key.isspace():
            errors.append("COHERE_API_KEY environment variable is required and cannot be empty")

        if errors:
            raise ValueError("; ".join(errors))


# Create global settings instance
def get_settings() -> Settings:
    """Get application settings"""
    try:
        settings = Settings()
        print(f"✅ Settings loaded successfully")
        print(f"   - Qdrant URL: {settings.qdrant_url}")
        print(f"   - Collection: {settings.qdrant_collection_name}")
        print(f"   - Embedding model: {settings.embedding_model}")
        print(f"   - API host: {settings.api_host}:{settings.api_port}")
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease ensure all required environment variables are set in .env file:")
        print("  - QDRANT_API_KEY: Your Qdrant cloud API key")
        print("  - QDRANT_URL: Your Qdrant cloud URL")
        print("  - COHERE_API_KEY: Your Cohere API key")
        raise

    return settings


# Initialize settings on module load
try:
    settings = get_settings()
except ValueError as e:
    print(f"❌ Failed to initialize settings: {e}")
    raise
