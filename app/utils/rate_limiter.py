"""Rate limiting utility for API endpoints."""
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
from fastapi import HTTPException, status


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Tracks requests per user and enforces limits.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store: {username: [(timestamp1, timestamp2, ...)]}
        self.requests: Dict[str, list] = defaultdict(list)

    def _clean_old_requests(self, username: str, current_time: float):
        """Remove requests older than the time window."""
        cutoff_time = current_time - self.window_seconds
        self.requests[username] = [
            req_time for req_time in self.requests[username]
            if req_time > cutoff_time
        ]

    def check_rate_limit(self, username: str) -> Tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.

        Args:
            username: Username to check

        Returns:
            Tuple of (is_allowed, requests_made, requests_remaining)
        """
        current_time = time.time()

        # Clean old requests
        self._clean_old_requests(username, current_time)

        # Count requests in current window
        requests_made = len(self.requests[username])

        # Check if limit exceeded
        is_allowed = requests_made < self.max_requests
        requests_remaining = max(0, self.max_requests - requests_made)

        return is_allowed, requests_made, requests_remaining

    def record_request(self, username: str):
        """
        Record a new request for the user.

        Args:
            username: Username making the request

        Raises:
            HTTPException: If rate limit exceeded
        """
        is_allowed, requests_made, requests_remaining = self.check_rate_limit(username)

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.max_requests} requests per {self.window_seconds} seconds. Try again later.",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.window_seconds))
                }
            )

        # Record the request
        self.requests[username].append(time.time())

    def get_rate_limit_info(self, username: str) -> Dict[str, int]:
        """
        Get rate limit information for a user.

        Args:
            username: Username to check

        Returns:
            Dictionary with limit info
        """
        is_allowed, requests_made, requests_remaining = self.check_rate_limit(username)

        return {
            "limit": self.max_requests,
            "remaining": requests_remaining,
            "used": requests_made,
            "window_seconds": self.window_seconds
        }


# Global rate limiter instance
# Configuration: 20 requests per minute
rate_limiter = RateLimiter(max_requests=20, window_seconds=60)
