"""Tests for the Riksdag feature.

These tests hit the real Riksdag API (no auth required, public data).
Use sparingly in CI — mark with @pytest.mark.integration if needed.
"""

from __future__ import annotations

from mcp_sweden.data.riksdag import client, tools


class TestClient:
    """Test the raw Riksdag API client."""

    async def test_search_documents_returns_dict(self) -> None:
        result = await client.search_documents(query="budget", page_size=2)
        assert isinstance(result, dict)
        assert "dokumentlista" in result

    async def test_list_members_returns_dict(self) -> None:
        result = await client.list_members(party="S")
        assert isinstance(result, dict)
        assert "personlista" in result

    async def test_search_votes_returns_dict(self) -> None:
        result = await client.search_votes(session="2024/25", page_size=2)
        assert isinstance(result, dict)
        assert "voteringlista" in result

    async def test_search_speeches_returns_dict(self) -> None:
        result = await client.search_speeches(query="klimat", page_size=2)
        assert isinstance(result, dict)
        assert "anforandelista" in result


class TestTools:
    """Test the tool functions (formatted output)."""

    async def test_search_documents_formatted(self) -> None:
        result = await tools.search_documents(query="budget", page_size=3)
        assert isinstance(result, str)
        assert "Found" in result or "No documents" in result

    async def test_list_members_by_party(self) -> None:
        result = await tools.list_members(party="M")
        assert isinstance(result, str)
        assert "Found" in result or "No members" in result

    async def test_search_votes_formatted(self) -> None:
        result = await tools.search_votes(session="2024/25", page_size=3)
        assert isinstance(result, str)
        assert "Found" in result or "No votes" in result

    async def test_search_speeches_formatted(self) -> None:
        result = await tools.search_speeches(query="utbildning", page_size=3)
        assert isinstance(result, str)
        assert "Found" in result or "No speeches" in result
