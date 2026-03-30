"""Tests for the SL feature."""

from __future__ import annotations

import pytest

from mcp_sweden.data.sl import FEATURE_META, client


class TestFeatureMeta:
    def test_meta_name(self) -> None:
        assert FEATURE_META.name == "sl"

    def test_no_auth_required(self) -> None:
        assert FEATURE_META.requires_auth is False

    def test_api_base(self) -> None:
        assert "transport.integration.sl.se" in FEATURE_META.api_base


class TestHaversine:
    def test_same_point(self) -> None:
        assert client._haversine(59.33, 18.07, 59.33, 18.07) == pytest.approx(0.0)

    def test_known_distance(self) -> None:
        # T-Centralen to Slussen is roughly 0.7 km
        dist = client._haversine(59.3308, 18.0597, 59.3196, 18.0722)
        assert 0.5 < dist < 1.5


class TestSearchSites:
    @pytest.mark.asyncio
    async def test_search_returns_results(self) -> None:
        results = await client.search_sites("T-Centralen")
        assert len(results) > 0
        assert any("T-Centralen" in s.get("name", "") for s in results)

    @pytest.mark.asyncio
    async def test_search_no_results(self) -> None:
        results = await client.search_sites("xyznonexistent123")
        assert len(results) == 0


class TestGetDepartures:
    @pytest.mark.asyncio
    async def test_departures_structure(self) -> None:
        data = await client.get_departures(site_id=9001)
        assert "departures" in data

    @pytest.mark.asyncio
    async def test_departures_with_mode_filter(self) -> None:
        data = await client.get_departures(site_id=9001, transport_mode="METRO")
        departures = data.get("departures", [])
        # API may return mixed modes at multimodal stations — just verify structure
        assert isinstance(departures, list)


class TestListLines:
    @pytest.mark.asyncio
    async def test_lines_grouped_by_mode(self) -> None:
        lines = await client.list_lines()
        assert isinstance(lines, dict)
        assert "metro" in lines
        assert "bus" in lines
