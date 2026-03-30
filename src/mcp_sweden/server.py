"""mcp-sweden root server — auto-discovers and mounts all features.

You should NEVER need to edit this file to add a new feature.
Just create a new directory under data/ following the convention.

Usage:
    fastmcp run mcp_sweden.server:mcp
    fastmcp run mcp_sweden.server:mcp --transport http --port 8000
"""

import logging
import time

import mcp.types as mt
from fastmcp import FastMCP
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from fastmcp.tools import ToolResult

from ._shared.feature import FeatureRegistry
from .settings import MCP_SWEDEN_API_TOKEN, TOOL_SEARCH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("mcp-sweden")


# ---------------------------------------------------------------------------
# Middleware — lightweight request logging
# ---------------------------------------------------------------------------
class RequestLoggingMiddleware(Middleware):
    """Log all tool calls with timing."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[mt.CallToolRequestParams],
        call_next: CallNext[mt.CallToolRequestParams, ToolResult],
    ) -> ToolResult:
        name = context.message.name
        logger.info("Tool call: %s", name)
        start = time.monotonic()
        result = await call_next(context)
        elapsed = time.monotonic() - start
        logger.info("Tool %s completed in %.2fs", name, elapsed)
        return result


# ---------------------------------------------------------------------------
# Authentication — conditional on MCP_SWEDEN_API_TOKEN
# ---------------------------------------------------------------------------
auth = None
if MCP_SWEDEN_API_TOKEN:
    from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

    auth = StaticTokenVerifier(
        tokens={
            MCP_SWEDEN_API_TOKEN: {
                "client_id": "mcp-client",
                "scopes": ["read"],
            }
        }
    )
    logger.info("Auth enabled: StaticTokenVerifier (Bearer token required)")

# ---------------------------------------------------------------------------
# Server setup
# ---------------------------------------------------------------------------

mcp = FastMCP("mcp-sweden 🇸🇪", auth=auth)
mcp.add_middleware(RequestLoggingMiddleware())


# Auto-discover and mount all features
registry = FeatureRegistry()
registry.discover("mcp_sweden.data")
registry.mount_all(mcp)

logger.info("\n%s", registry.summary())


# Meta-tool for introspection
@mcp.tool(tags={"meta", "discovery"})
def list_features() -> str:
    """List all available features (data sources) in mcp-sweden.

    Use this tool to see which Swedish APIs are connected
    and what tools each one offers.

    Returns:
        Summary of active features with descriptions and auth status.
    """
    return registry.summary()


# ---------------------------------------------------------------------------
# Tool Search Transform
# ---------------------------------------------------------------------------
_always_visible = ["list_features"]

if TOOL_SEARCH == "bm25":
    from fastmcp.server.transforms.search import BM25SearchTransform

    mcp.add_transform(
        BM25SearchTransform(
            max_results=10,
            always_visible=_always_visible,
        )
    )
    logger.info("Tool search: BM25 (search_tools + call_tool)")
else:
    logger.info("Tool search: none (all tools visible)")


if __name__ == "__main__":
    mcp.run()
