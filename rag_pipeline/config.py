"""Configuration loading for RAG pipeline."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for RAG pipeline."""

    def __init__(self, env_file: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            env_file: Path to .env file (default: .env)
            config_file: Path to config.yaml (default: config.yaml)
        """
        # Load environment variables
        if env_file is None:
            env_file = ".env"
        if Path(env_file).exists():
            load_dotenv(env_file)

        # Validate required environment variables
        self._validate_required_vars()

        # Load configuration file if present
        self.config_data = {}
        if config_file is None:
            config_file = "config.yaml"
        if Path(config_file).exists():
            with open(config_file) as f:
                self.config_data = yaml.safe_load(f) or {}

    def _validate_required_vars(self) -> None:
        """Validate required environment variables are present."""
        required = ["COHERE_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"]
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to environment variable."""
        # First check environment
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return env_value

        # Then check config file
        if key in self.config_data:
            return self.config_data[key]

        return default

    @property
    def cohere_api_key(self) -> str:
        """Get Cohere API key."""
        return os.getenv("COHERE_API_KEY", "")

    @property
    def cohere_model(self) -> str:
        """Get Cohere model name."""
        return self.get("cohere_model", "embed-english-v3.0")

    @property
    def qdrant_url(self) -> str:
        """Get Qdrant URL."""
        return os.getenv("QDRANT_URL", "")

    @property
    def qdrant_api_key(self) -> str:
        """Get Qdrant API key."""
        return os.getenv("QDRANT_API_KEY", "")

    @property
    def qdrant_collection(self) -> str:
        """Get Qdrant collection name."""
        return self.get("qdrant_collection", "documents")

    @property
    def target_website_url(self) -> str:
        """Get target website URL to crawl."""
        return os.getenv("TARGET_WEBSITE_URL", "")

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO")

    def get_crawler_config(self) -> Dict[str, Any]:
        """Get crawler configuration."""
        return self.config_data.get(
            "crawler",
            {
                "base_url": self.target_website_url,
                "request_delay": 0.5,
                "timeout": 10,
                "max_pages": None,
                "respect_robots_txt": True,
                "user_agent": "RAGCrawler/1.0",
            },
        )

    def get_chunking_config(self) -> Dict[str, Any]:
        """Get text chunking configuration."""
        return self.config_data.get(
            "chunking",
            {
                "min_tokens": 100,
                "target_tokens": 350,
                "max_tokens": 512,
                "overlap_tokens": 50,
            },
        )

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding generation configuration."""
        return self.config_data.get(
            "embedding",
            {
                "api_key": self.cohere_api_key,
                "model": self.cohere_model,
                "embedding_dimension": 1024,
                "batch_size": 100,
                "retry_max_attempts": 5,
                "retry_initial_delay": 1,
            },
        )

    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration."""
        return self.config_data.get(
            "retry",
            {
                "max_attempts": 5,
                "initial_delay": 1,
                "exponential_base": 2,
                "max_delay": 60,
            },
        )


def create_config(env_file: Optional[str] = None, config_file: Optional[str] = None) -> Config:
    """Factory function to create Config instance."""
    return Config(env_file, config_file)
