"""HTTP client for the Avanza API.

Avanza's public (non-authenticated) API provides stock quotes, fund data,
market indices, and search across the OMX Stockholm exchange.

API base: https://www.avanza.se/_api
Key endpoints:
    - Search: GET /search/global-search/global-search-template?query={query}
    - Stock: GET /market-guide/stock/{orderbookId}
    - Fund: GET /fund-guide/guide/{orderbookId}
    - Chart: GET /price-chart/stock/{orderbookId}?timePeriod={period}
    - Orderbook: GET /orderbook/{type}/{orderbookId}
    - Index: GET /market-guide/stock/index/summary

Reference: https://github.com/AnteWall/avanza-mcp
"""

from __future__ import annotations

from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

API_BASE = "https://www.avanza.se/_api"

# Custom headers — Avanza's API expects browser-like requests
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; mcp-sweden/0.1.0)",
    "Accept": "application/json",
}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@ttl_cache(ttl=120)
async def search(query: str, limit: int = 10) -> Any:
    """Search for stocks, funds, indices, and other instruments."""
    return await http_get(
        f"{API_BASE}/search/global-search/global-search-template",
        params={"query": query, "limit": limit},
        headers=_HEADERS,
    )


# ---------------------------------------------------------------------------
# Stocks
# ---------------------------------------------------------------------------


@ttl_cache(ttl=60)
async def get_stock(orderbook_id: str) -> Any:
    """Get detailed stock information including price, change, and key figures."""
    return await http_get(
        f"{API_BASE}/market-guide/stock/{orderbook_id}",
        headers=_HEADERS,
    )


@ttl_cache(ttl=60)
async def get_stock_chart(
    orderbook_id: str,
    time_period: str = "one_month",
) -> Any:
    """Get price chart data for a stock.

    Args:
        orderbook_id: The instrument's orderbook ID.
        time_period: One of: today, one_week, one_month, three_months,
                     this_year, one_year, three_years, five_years, infinity.
    """
    return await http_get(
        f"{API_BASE}/price-chart/stock/{orderbook_id}",
        params={"timePeriod": time_period},
        headers=_HEADERS,
    )


@ttl_cache(ttl=60)
async def get_orderbook(orderbook_id: str, orderbook_type: str = "stock") -> Any:
    """Get the orderbook (buy/sell depth) for an instrument.

    Args:
        orderbook_id: The instrument's orderbook ID.
        orderbook_type: Type of orderbook: stock, fund, index, etc.
    """
    return await http_get(
        f"{API_BASE}/orderbook/{orderbook_type}/{orderbook_id}",
        headers=_HEADERS,
    )


# ---------------------------------------------------------------------------
# Funds
# ---------------------------------------------------------------------------


@ttl_cache(ttl=300)
async def get_fund(orderbook_id: str) -> Any:
    """Get detailed fund information including NAV, fees, and holdings."""
    return await http_get(
        f"{API_BASE}/fund-guide/guide/{orderbook_id}",
        headers=_HEADERS,
    )


# ---------------------------------------------------------------------------
# Market Overview / Indices
# ---------------------------------------------------------------------------


@ttl_cache(ttl=120)
async def get_market_overview() -> Any:
    """Get market overview with major indices and movers."""
    return await http_get(
        f"{API_BASE}/market-guide/stock/index/summary",
        headers=_HEADERS,
    )


@ttl_cache(ttl=60)
async def get_index(orderbook_id: str) -> Any:
    """Get details for a market index (e.g. OMXS30)."""
    return await http_get(
        f"{API_BASE}/market-guide/stock/{orderbook_id}",
        headers=_HEADERS,
    )
