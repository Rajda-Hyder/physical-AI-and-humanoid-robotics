"""Exponential backoff retry logic for API calls."""

import time
from typing import Optional


class ExponentialBackoff:
    """Implements exponential backoff retry strategy."""

    def __init__(
        self,
        initial_delay: float = 1.0,
        max_attempts: int = 5,
        base: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        Initialize exponential backoff.

        Args:
            initial_delay: Starting delay in seconds
            max_attempts: Maximum number of retry attempts
            base: Exponential base for calculation
            max_delay: Maximum delay cap in seconds
        """
        self.initial_delay = initial_delay
        self.max_attempts = max_attempts
        self.base = base
        self.max_delay = max_delay
        self.attempt = 0

    def should_retry(self, exception: Exception) -> bool:
        """Determine if an exception should be retried."""
        # Retry on network and server errors
        retryable_types = (
            ConnectionError,
            TimeoutError,
            OSError,
        )
        return isinstance(exception, retryable_types) and self.attempt < self.max_attempts

    def get_next_delay(self) -> float:
        """Calculate next delay using exponential backoff."""
        if self.attempt >= self.max_attempts:
            return 0
        delay = self.initial_delay * (self.base ** self.attempt)
        return min(delay, self.max_delay)

    def wait(self) -> None:
        """Sleep for the calculated delay."""
        delay = self.get_next_delay()
        if delay > 0:
            time.sleep(delay)
        self.attempt += 1

    def reset(self) -> None:
        """Reset attempt counter."""
        self.attempt = 0
