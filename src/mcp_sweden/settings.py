"""Global configuration for mcp-sweden.

Values can be overridden via environment variables.
Automatically loads .env from the project root.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- HTTP Client ---
HTTP_TIMEOUT: float = float(os.environ.get("MCP_SWEDEN_HTTP_TIMEOUT", "30.0"))
HTTP_MAX_RETRIES: int = int(os.environ.get("MCP_SWEDEN_HTTP_MAX_RETRIES", "3"))
HTTP_BACKOFF_BASE: float = float(os.environ.get("MCP_SWEDEN_HTTP_BACKOFF_BASE", "1.0"))
USER_AGENT: str = os.environ.get("MCP_SWEDEN_USER_AGENT", "mcp-sweden/0.1.0")

# --- Tool Discovery ---
# "bm25" (default): BM25 search transform
# "none": No transform — all tools visible at once
TOOL_SEARCH: str = os.environ.get("MCP_SWEDEN_TOOL_SEARCH", "bm25")

# --- Authentication ---
MCP_SWEDEN_API_TOKEN: str | None = os.environ.get("MCP_SWEDEN_API_TOKEN") or None

# --- LLM Discovery ---
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
