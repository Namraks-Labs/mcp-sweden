"""Tool implementations for the Avanza feature.

Each function becomes an MCP tool registered in server.py.
Provides access to Swedish stock market data via Avanza's public API.
"""

from __future__ import annotations

import json
from typing import Any

from . import client


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


async def search_instruments(query: str, limit: int = 10) -> str:
    """Search for Swedish stocks, funds, indices, and other financial instruments on Avanza.

    Covers OMX Stockholm (Stockholmsbörsen) and Nasdaq Nordic listed securities.

    Args:
        query: Search term — company name, ticker symbol, or ISIN
               (e.g. "Volvo", "ERIC B", "Handelsbanken", "SE0000108656").
        limit: Maximum results per category (default: 10).

    Returns:
        JSON with matching instruments grouped by type (stocks, funds, indices, etc.),
        including orderbook IDs needed for other tools.
    """
    data = await client.search(query, limit=limit)
    if not data:
        return f"No results found for '{query}'."

    results: dict[str, Any] = {}

    # The search response groups results by type
    for section_key in ("resultGroups", "hits"):
        sections = data.get(section_key, [])
        if not isinstance(sections, list):
            continue
        for section in sections:
            instrument_type = section.get("instrumentType", section.get("type", "unknown"))
            hits = section.get("hits", section.get("topHits", []))
            if not hits:
                continue
            items = []
            for hit in hits:
                entry: dict[str, Any] = {
                    "name": hit.get("name", hit.get("tickerSymbol", "")),
                    "orderbook_id": hit.get("id", hit.get("orderbookId", "")),
                }
                if hit.get("tickerSymbol"):
                    entry["ticker"] = hit["tickerSymbol"]
                if hit.get("lastPrice") is not None:
                    entry["last_price"] = hit["lastPrice"]
                if hit.get("changePercent") is not None:
                    entry["change_percent"] = hit["changePercent"]
                if hit.get("flagCode"):
                    entry["country"] = hit["flagCode"]
                items.append(entry)
            results[instrument_type] = items

    if not results:
        # Fallback: return raw data structure if format is unexpected
        return _json({"query": query, "raw": data})

    return _json({"query": query, "results": results})


# ---------------------------------------------------------------------------
# Stock Info
# ---------------------------------------------------------------------------


async def get_stock_info(orderbook_id: str) -> str:
    """Get detailed information about a Swedish stock.

    Includes current price, daily change, volume, market cap, P/E ratio,
    dividend yield, 52-week high/low, and company description.

    Args:
        orderbook_id: The stock's orderbook ID (find with search_instruments).

    Returns:
        JSON with comprehensive stock data from Avanza.
    """
    data = await client.get_stock(orderbook_id)
    if not data:
        return f"No stock data found for orderbook ID {orderbook_id}."

    # Extract key fields, handling Avanza's nested response
    listing = data.get("listing", data)
    key_ratios = data.get("keyRatios", {})
    company = data.get("company", {})

    result: dict[str, Any] = {
        "name": listing.get("name", data.get("name", "")),
        "ticker": listing.get("tickerSymbol", data.get("tickerSymbol", "")),
        "currency": listing.get("currency", data.get("currency", "")),
        "marketplace": listing.get("marketplaceName", data.get("marketPlace", "")),
    }

    # Price data
    quote = data.get("quote", listing)
    if quote:
        result["last_price"] = quote.get("last", quote.get("lastPrice"))
        result["change"] = quote.get("change")
        result["change_percent"] = quote.get("changePercent")
        result["highest"] = quote.get("highest", quote.get("highestPrice"))
        result["lowest"] = quote.get("lowest", quote.get("lowestPrice"))
        result["volume"] = quote.get("totalVolumeTraded")

    # Key ratios
    if key_ratios:
        result["pe_ratio"] = key_ratios.get("priceEarningsRatio")
        result["ps_ratio"] = key_ratios.get("priceSalesRatio")
        result["dividend_yield"] = key_ratios.get("directYield")
        result["volatility"] = key_ratios.get("volatility")
        result["market_cap"] = key_ratios.get("marketCapital")

    # Company info
    if company:
        result["sector"] = company.get("sector", "")
        result["description"] = company.get("description", "")
        if company.get("ceo"):
            result["ceo"] = company["ceo"]
        if company.get("totalNumberOfShares"):
            result["total_shares"] = company["totalNumberOfShares"]

    # Clean out None values
    result = {k: v for k, v in result.items() if v is not None}

    return _json(result)


# ---------------------------------------------------------------------------
# Fund Info
# ---------------------------------------------------------------------------


async def get_fund_info(orderbook_id: str) -> str:
    """Get detailed information about a Swedish investment fund.

    Includes NAV (net asset value), management fee, risk level,
    performance history, top holdings, and fund category.

    Args:
        orderbook_id: The fund's orderbook ID (find with search_instruments).

    Returns:
        JSON with comprehensive fund data from Avanza.
    """
    data = await client.get_fund(orderbook_id)
    if not data:
        return f"No fund data found for orderbook ID {orderbook_id}."

    result: dict[str, Any] = {
        "name": data.get("name", ""),
        "nav": data.get("nav", data.get("NAV")),
        "nav_date": data.get("navDate"),
        "currency": data.get("currency", ""),
    }

    # Fees
    if data.get("productFee") is not None:
        result["management_fee_percent"] = data["productFee"]
    elif data.get("managementFee") is not None:
        result["management_fee_percent"] = data["managementFee"]

    # Performance
    perf: dict[str, Any] = {}
    for key, label in [
        ("developmentOneDay", "1d"),
        ("developmentOneMonth", "1m"),
        ("developmentThreeMonths", "3m"),
        ("developmentSixMonths", "6m"),
        ("developmentOneYear", "1y"),
        ("developmentThreeYears", "3y"),
        ("developmentFiveYears", "5y"),
        ("developmentThisYear", "ytd"),
    ]:
        val = data.get(key)
        if val is not None:
            perf[label] = val
    if perf:
        result["performance_percent"] = perf

    # Risk
    result["risk"] = data.get("risk")
    result["risk_level"] = data.get("riskLevel")
    result["sharpe_ratio"] = data.get("sharpeRatio")
    result["standard_deviation"] = data.get("standardDeviation")

    # Category
    result["category"] = data.get("subCategory", data.get("category", ""))
    result["type"] = data.get("type", "")

    # Top holdings
    holdings = data.get("topHoldings", [])
    if holdings:
        result["top_holdings"] = [
            {
                "name": h.get("name", ""),
                "country": h.get("countryCode", ""),
                "percent": h.get("holdingPercent"),
            }
            for h in holdings[:10]
        ]

    # Clean out None values
    result = {k: v for k, v in result.items() if v is not None}

    return _json(result)


# ---------------------------------------------------------------------------
# Price Chart
# ---------------------------------------------------------------------------


async def get_price_chart(
    orderbook_id: str,
    time_period: str = "one_month",
) -> str:
    """Get historical price chart data for a stock or index.

    Useful for analyzing price trends over different time horizons.

    Args:
        orderbook_id: The instrument's orderbook ID (find with search_instruments).
        time_period: Chart period — one of: today, one_week, one_month,
                     three_months, this_year, one_year, three_years,
                     five_years, infinity.

    Returns:
        JSON with OHLC data points, comparison indices, and period summary.
    """
    data = await client.get_stock_chart(orderbook_id, time_period=time_period)
    if not data:
        return f"No chart data for orderbook ID {orderbook_id} ({time_period})."

    result: dict[str, Any] = {
        "orderbook_id": orderbook_id,
        "time_period": time_period,
    }

    # Data points
    ohlc = data.get("ohlc", [])
    data_points = data.get("dataSerie", data.get("dataPoints", []))

    if ohlc:
        result["data_point_count"] = len(ohlc)
        # Return first and last few points + summary rather than flooding
        if len(ohlc) > 10:
            result["first_point"] = ohlc[0]
            result["last_point"] = ohlc[-1]
            result["sample_points"] = ohlc[:: max(1, len(ohlc) // 10)]
        else:
            result["data_points"] = ohlc
    elif data_points:
        result["data_point_count"] = len(data_points)
        if len(data_points) > 10:
            result["first_point"] = data_points[0]
            result["last_point"] = data_points[-1]
            result["sample_points"] = data_points[:: max(1, len(data_points) // 10)]
        else:
            result["data_points"] = data_points

    # Period summary
    for key in ("change", "changePercent", "min", "max", "from", "to"):
        if data.get(key) is not None:
            result[key] = data[key]

    # Comparison indices
    comparisons = data.get("comparisonSeries", [])
    if comparisons:
        result["comparisons"] = [
            {"name": c.get("name", ""), "data_points": len(c.get("dataSerie", []))}
            for c in comparisons
        ]

    return _json(result)


# ---------------------------------------------------------------------------
# Orderbook (Buy/Sell Depth)
# ---------------------------------------------------------------------------


async def get_orderbook_depth(orderbook_id: str) -> str:
    """Get the orderbook (buy/sell depth) for a stock on OMX Stockholm.

    Shows current bid/ask levels, total buy/sell volume, and spread.
    Useful for understanding liquidity and market sentiment.

    Args:
        orderbook_id: The stock's orderbook ID (find with search_instruments).

    Returns:
        JSON with orderbook levels, latest trades, and spread information.
    """
    data = await client.get_orderbook(orderbook_id, orderbook_type="stock")
    if not data:
        return f"No orderbook data for {orderbook_id}."

    result: dict[str, Any] = {
        "orderbook_id": orderbook_id,
    }

    # Name and basic info
    orderbook = data.get("orderbook", data)
    result["name"] = orderbook.get("name", "")
    result["last_price"] = orderbook.get("lastPrice")
    result["change"] = orderbook.get("change")
    result["change_percent"] = orderbook.get("changePercent")
    result["total_volume"] = orderbook.get("totalVolumeTraded")
    result["updated"] = orderbook.get("updated", "")

    # Buy/Sell levels
    buy_levels = data.get("orderDepthLevels", data.get("orderDepth", []))
    if isinstance(buy_levels, list):
        result["depth_levels"] = buy_levels[:10]
    elif isinstance(buy_levels, dict):
        result["buy_levels"] = buy_levels.get("buy", [])[:5]
        result["sell_levels"] = buy_levels.get("sell", [])[:5]

    # Latest trades
    latest_trades = data.get("latestTrades", [])
    if latest_trades:
        result["latest_trades"] = [
            {
                "price": t.get("price"),
                "volume": t.get("volume"),
                "time": t.get("dealTime", ""),
                "buyer": t.get("buyer", ""),
                "seller": t.get("seller", ""),
            }
            for t in latest_trades[:5]
        ]

    # Clean out None values
    result = {k: v for k, v in result.items() if v is not None}

    return _json(result)


# ---------------------------------------------------------------------------
# Market Overview
# ---------------------------------------------------------------------------


async def get_market_overview() -> str:
    """Get a snapshot of the Swedish stock market.

    Shows major indices (OMXS30, OMXSPI, etc.), market status,
    and top movers on Stockholmsbörsen.

    Returns:
        JSON with index levels, daily changes, and market summary.
    """
    data = await client.get_market_overview()
    if not data:
        return "No market overview data available."

    return _json(data)
