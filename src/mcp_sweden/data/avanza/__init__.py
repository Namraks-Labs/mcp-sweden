"""Feature: Avanza — Swedish Stock Market & Financial Data."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="avanza",
    description="Avanza: stock quotes, funds, market data, orderbook, charts",
    version="0.1.0",
    api_base="https://www.avanza.se/_api",
    requires_auth=False,
    tags=["finance", "stocks", "funds", "market", "trading"],
)
