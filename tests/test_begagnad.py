"""Tests for the Begagnad (second-hand marketplaces) feature."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_sweden.data.begagnad import FEATURE_META
from mcp_sweden.data.begagnad.client import (
    _element_to_dict,
    _parse_xml_to_dict,
    is_tradera_available,
)
from mcp_sweden.data.begagnad.tools import (
    get_blocket_item,
    search_begagnad,
    search_blocket,
    search_tradera,
)


class TestFeatureMeta:
    def test_meta_name(self) -> None:
        assert FEATURE_META.name == "begagnad"

    def test_no_auth_required(self) -> None:
        assert FEATURE_META.requires_auth is False

    def test_tags(self) -> None:
        assert "marketplace" in FEATURE_META.tags
        assert "second-hand" in FEATURE_META.tags


class TestXmlParsing:
    def test_simple_xml(self) -> None:
        xml = "<root><name>Test</name><value>42</value></root>"
        result = _parse_xml_to_dict(xml)
        assert result["name"] == "Test"
        assert result["value"] == "42"

    def test_nested_xml(self) -> None:
        xml = "<root><item><id>1</id><title>Lamp</title></item></root>"
        result = _parse_xml_to_dict(xml)
        assert result["item"]["id"] == "1"
        assert result["item"]["title"] == "Lamp"

    def test_namespace_stripping(self) -> None:
        xml = '<root xmlns:a="http://example.com"><a:name>Test</a:name></root>'
        result = _parse_xml_to_dict(xml)
        assert result["name"] == "Test"


class TestTraderaAvailability:
    def test_unavailable_without_env(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            assert is_tradera_available() is False

    def test_available_with_env(self) -> None:
        with patch.dict(
            "os.environ",
            {"TRADERA_APP_ID": "test-id", "TRADERA_APP_KEY": "test-key"},
        ):
            assert is_tradera_available() is True


class TestSearchBlocket:
    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        from mcp_sweden.data.begagnad.client import search_blocket as fn
        if hasattr(fn, "cache"):
            fn.cache.clear()

    @pytest.mark.asyncio
    async def test_returns_formatted_json(self) -> None:
        mock_items = [
            {
                "id": "123",
                "title": "Test Item",
                "price": 500.0,
                "source": "blocket",
            }
        ]
        with patch(
            "mcp_sweden.data.begagnad.client.search_blocket",
            new_callable=AsyncMock,
            return_value=mock_items,
        ):
            result = await search_blocket("test")
            assert '"count": 1' in result
            assert "blocket" in result

    @pytest.mark.asyncio
    async def test_empty_results(self) -> None:
        with patch(
            "mcp_sweden.data.begagnad.client.search_blocket",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await search_blocket("nonexistent")
            assert "No Blocket listings found" in result


class TestSearchTradera:
    @pytest.mark.asyncio
    async def test_unavailable_message(self) -> None:
        with patch(
            "mcp_sweden.data.begagnad.client.is_tradera_available",
            return_value=False,
        ):
            result = await search_tradera("test")
            assert "unavailable" in result

    @pytest.mark.asyncio
    async def test_returns_results_when_available(self) -> None:
        mock_items = [
            {
                "id": "456",
                "title": "Auction Item",
                "price": 100.0,
                "source": "tradera",
            }
        ]
        with patch(
            "mcp_sweden.data.begagnad.client.is_tradera_available",
            return_value=True,
        ), patch(
            "mcp_sweden.data.begagnad.client.search_tradera",
            new_callable=AsyncMock,
            return_value=mock_items,
        ):
            result = await search_tradera("test")
            assert '"count": 1' in result
            assert "tradera" in result


class TestSearchBegagnad:
    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        from mcp_sweden.data.begagnad.client import search_blocket as fn
        if hasattr(fn, "cache"):
            fn.cache.clear()

    @pytest.mark.asyncio
    async def test_combined_search(self) -> None:
        blocket_items = [{"id": "1", "title": "Blocket item", "source": "blocket"}]
        tradera_items = [{"id": "2", "title": "Tradera item", "source": "tradera"}]

        with patch(
            "mcp_sweden.data.begagnad.client.search_blocket",
            new_callable=AsyncMock,
            return_value=blocket_items,
        ), patch(
            "mcp_sweden.data.begagnad.client.is_tradera_available",
            return_value=True,
        ), patch(
            "mcp_sweden.data.begagnad.client.search_tradera",
            new_callable=AsyncMock,
            return_value=tradera_items,
        ):
            result = await search_begagnad("test")
            assert '"total": 2' in result
            assert '"blocket_count": 1' in result
            assert '"tradera_count": 1' in result

    @pytest.mark.asyncio
    async def test_blocket_only_when_tradera_unavailable(self) -> None:
        blocket_items = [{"id": "1", "title": "Item", "source": "blocket"}]

        with patch(
            "mcp_sweden.data.begagnad.client.search_blocket",
            new_callable=AsyncMock,
            return_value=blocket_items,
        ), patch(
            "mcp_sweden.data.begagnad.client.is_tradera_available",
            return_value=False,
        ):
            result = await search_begagnad("test")
            assert '"total": 1' in result
            assert '"tradera_count": 0' in result
            assert "credentials not configured" in result


class TestGetBlocketItem:
    @pytest.fixture(autouse=True)
    def _clear_cache(self) -> None:
        from mcp_sweden.data.begagnad.client import get_blocket_item as fn
        if hasattr(fn, "cache"):
            fn.cache.clear()

    @pytest.mark.asyncio
    async def test_returns_item(self) -> None:
        mock_item = {"id": "123", "title": "Cool item", "source": "blocket"}
        with patch(
            "mcp_sweden.data.begagnad.client.get_blocket_item",
            new_callable=AsyncMock,
            return_value=mock_item,
        ):
            result = await get_blocket_item("123")
            assert "Cool item" in result
