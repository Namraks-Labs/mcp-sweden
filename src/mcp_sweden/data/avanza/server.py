"""Avanza feature server — registers tools for Swedish financial market data.

Reference: https://github.com/AnteWall/avanza-mcp
API: https://www.avanza.se/_api (public, no auth required)
"""

from fastmcp import FastMCP

from .tools import (
    get_fund_info,
    get_market_overview,
    get_orderbook_depth,
    get_price_chart,
    get_stock_info,
    search_instruments,
)

mcp = FastMCP("mcp-sweden-avanza")

# Search & Discovery
mcp.tool(search_instruments, tags={"search", "discovery", "stocks", "funds"})

# Stock Data
mcp.tool(get_stock_info, tags={"stocks", "quotes", "company"})
mcp.tool(get_price_chart, tags={"stocks", "charts", "history"})
mcp.tool(get_orderbook_depth, tags={"stocks", "orderbook", "trading"})

# Fund Data
mcp.tool(get_fund_info, tags={"funds", "nav", "holdings"})

# Market Overview
mcp.tool(get_market_overview, tags={"market", "indices", "overview"})
