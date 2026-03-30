"""Simple async rate limiter for API calls.

Usage:
    from mcp_sweden._shared.rate_limiter import RateLimiter

    limiter = RateLimiter(max_calls=10, period=60.0)

    async def fetch_data():
        async with limiter:
            return await http_get(...)
"""

from __future__ import annotations

import asyncio
import time
from collections import deque


class RateLimiter:
    """Token-bucket rate limiter for async code."""

    def __init__(self, max_calls: int = 10, period: float = 60.0) -> None:
        self._max_calls = max_calls
        self._period = period
        self._calls: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> RateLimiter:
        async with self._lock:
            now = time.monotonic()
            while self._calls and now - self._calls[0] >= self._period:
                self._calls.popleft()

            if len(self._calls) >= self._max_calls:
                sleep_time = self._period - (now - self._calls[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                self._calls.popleft()

            self._calls.append(time.monotonic())
        return self

    async def __aexit__(self, *args: object) -> None:
        pass
