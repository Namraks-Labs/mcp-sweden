"""Simple async-safe TTL cache for API responses.

Usage:
    from mcp_sweden._shared.cache import ttl_cache

    cache = ttl_cache(ttl=300)  # 5 minutes

    @cache
    async def list_parties() -> list[dict]:
        ...  # HTTP call only happens on cache miss or expiry
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class TTLCache:
    """In-memory cache with per-entry TTL expiration."""

    def __init__(self, ttl: float = 300.0, maxsize: int = 256) -> None:
        self._ttl = ttl
        self._maxsize = maxsize
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self._maxsize:
            self._evict()
        self._store[key] = (time.monotonic() + self._ttl, value)

    def _evict(self) -> None:
        now = time.monotonic()
        expired = [k for k, (exp, _) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]
        if len(self._store) >= self._maxsize:
            oldest = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest]

    def clear(self) -> None:
        self._store.clear()


def ttl_cache(ttl: float = 300.0) -> Callable[[F], F]:
    """Decorator factory for async functions with TTL caching."""
    cache = TTLCache(ttl=ttl)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            cached = cache.get(key)
            if cached is not None:
                return cached
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result

        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
