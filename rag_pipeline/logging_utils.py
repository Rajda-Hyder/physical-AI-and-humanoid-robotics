"""Logging infrastructure for RAG pipeline."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class OperationLogger:
    """Structured logging for RAG pipeline operations."""

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """Initialize operation logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Set up file logger
        log_file = self.log_dir / f"ingestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.logger = logging.getLogger("rag_pipeline")
        self.logger.setLevel(getattr(logging, log_level))

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # JSON operations log
        self.ops_log_file = self.log_dir / f"operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"

    def log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Log structured operation data."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "details": details,
        }
        with open(self.ops_log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def log_info(self, message: str) -> None:
        """Log info level message."""
        self.logger.info(message)

    def log_error(self, message: str) -> None:
        """Log error level message."""
        self.logger.error(message)

    def log_warning(self, message: str) -> None:
        """Log warning level message."""
        self.logger.warning(message)

    def log_debug(self, message: str) -> None:
        """Log debug level message."""
        self.logger.debug(message)


# Global logger instance
_logger: OperationLogger = None


def get_logger(log_dir: str = "logs", log_level: str = "INFO") -> OperationLogger:
    """Get or create global logger instance."""
    global _logger
    if _logger is None:
        _logger = OperationLogger(log_dir, log_level)
    return _logger
