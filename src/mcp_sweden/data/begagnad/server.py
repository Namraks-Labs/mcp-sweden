"""Begagnad feature server — registers tools for second-hand marketplace data.

Sources:
    - Blocket (no auth): Sweden's largest classifieds
    - Tradera (optional auth): Sweden's largest auction site

Reference: https://github.com/bjesus/begagnad-mcp
"""

from fastmcp import FastMCP

from .tools import (
    get_blocket_item,
    get_tradera_item,
    search_begagnad,
    search_blocket,
    search_tradera,
)

mcp = FastMCP("mcp-sweden-begagnad")

# Combined search (recommended)
mcp.tool(search_begagnad, tags={"search", "marketplace", "blocket", "tradera"})

# Blocket
mcp.tool(search_blocket, tags={"search", "blocket", "classifieds"})
mcp.tool(get_blocket_item, tags={"blocket", "details", "classifieds"})

# Tradera
mcp.tool(search_tradera, tags={"search", "tradera", "auctions"})
mcp.tool(get_tradera_item, tags={"tradera", "details", "auctions"})
