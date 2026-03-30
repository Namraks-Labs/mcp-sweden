"""Tests for the Avanza feature — verifies tool registration and module structure."""

from __future__ import annotations

import importlib


def test_feature_meta_exists():
    """FEATURE_META is exported from the avanza package."""
    mod = importlib.import_module("mcp_sweden.data.avanza")
    meta = getattr(mod, "FEATURE_META", None)
    assert meta is not None
    assert meta.name == "avanza"
    assert meta.requires_auth is False


def test_server_has_mcp_object():
    """server.py exports an mcp FastMCP instance."""
    mod = importlib.import_module("mcp_sweden.data.avanza.server")
    mcp = getattr(mod, "mcp", None)
    assert mcp is not None


async def test_tools_are_registered():
    """All expected tools are registered on the server."""
    from mcp_sweden.data.avanza.server import mcp

    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    expected = {
        "search_instruments",
        "get_stock_info",
        "get_fund_info",
        "get_price_chart",
        "get_orderbook_depth",
        "get_market_overview",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


def test_client_functions_exist():
    """Client module exports the expected async functions."""
    from mcp_sweden.data.avanza import client

    expected_funcs = [
        "search",
        "get_stock",
        "get_stock_chart",
        "get_orderbook",
        "get_fund",
        "get_market_overview",
        "get_index",
    ]
    for func_name in expected_funcs:
        assert hasattr(client, func_name), f"Missing client function: {func_name}"
        assert callable(getattr(client, func_name))
