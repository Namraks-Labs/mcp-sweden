"""Shared async HTTP client for mcp-sweden.

Provides a configured httpx.AsyncClient factory and fetch helpers
with retry + exponential backoff for transient errors.

Usage:
    from mcp_sweden._shared.http_client import http_get

    data = await http_get("https://data.riksdagen.se/dokumentlista/")
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from mcp_sweden.exceptions import HttpClientError
from mcp_sweden.settings import HTTP_BACKOFF_BASE, HTTP_MAX_RETRIES, HTTP_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def create_client(
    base_url: str = "",
    timeout: float | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.AsyncClient:
    """Create a configured httpx.AsyncClient."""
    default_headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)

    return httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout or HTTP_TIMEOUT,
        headers=default_headers,
        follow_redirects=True,
    )


async def http_get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """GET with automatic retry on transient errors."""
    return await _fetch("GET", url, params=params, headers=headers)


async def http_post(
    url: str,
    json: Any = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """POST with automatic retry on transient errors."""
    return await _fetch("POST", url, json=json, params=params, headers=headers)


async def _fetch(
    method: str,
    url: str,
    params: dict[str, Any] | None = None,
    json: Any = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """Internal fetch with retry logic."""
    last_error: Exception | None = None

    async with create_client(headers=headers) as client:
        for attempt in range(HTTP_MAX_RETRIES + 1):
            try:
                response = await client.request(method, url, params=params, json=json)

                if response.status_code < 400:
                    content_type = response.headers.get("content-type", "")
                    if "json" in content_type:
                        return response.json()
                    return response.text

                if response.status_code in _RETRYABLE_STATUS_CODES:
                    last_error = HttpClientError(url, response.status_code)
                    logger.warning(
                        "Retryable %d from %s (attempt %d/%d)",
                        response.status_code,
                        url,
                        attempt + 1,
                        HTTP_MAX_RETRIES + 1,
                    )
                else:
                    raise HttpClientError(url, response.status_code, response.text[:200])

            except httpx.TimeoutException:
                last_error = HttpClientError(url, detail="timeout")
                logger.warning(
                    "Timeout for %s (attempt %d/%d)",
                    url,
                    attempt + 1,
                    HTTP_MAX_RETRIES + 1,
                )
            except HttpClientError:
                raise
            except httpx.HTTPError as exc:
                last_error = HttpClientError(url, detail=str(exc))
                logger.warning(
                    "HTTP error for %s: %s (attempt %d/%d)",
                    url,
                    exc,
                    attempt + 1,
                    HTTP_MAX_RETRIES + 1,
                )

            if attempt < HTTP_MAX_RETRIES:
                wait = HTTP_BACKOFF_BASE * (2**attempt)
                await asyncio.sleep(wait)

    raise last_error or HttpClientError(url, detail="unknown error")
