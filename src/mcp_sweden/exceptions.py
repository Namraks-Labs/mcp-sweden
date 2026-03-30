"""Shared exceptions for mcp-sweden."""

from __future__ import annotations


class McpSwedenError(Exception):
    """Base exception for all mcp-sweden errors."""


class HttpClientError(McpSwedenError):
    """Raised when an HTTP request fails after all retries."""

    def __init__(self, url: str, status_code: int | None = None, detail: str = "") -> None:
        self.url = url
        self.status_code = status_code
        self.detail = detail
        msg = f"HTTP error for {url}"
        if status_code:
            msg += f" (status {status_code})"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class FeatureError(McpSwedenError):
    """Raised when a feature fails to load or register."""
