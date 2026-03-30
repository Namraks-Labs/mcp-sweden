"""Tests for the Skolverket feature."""

from __future__ import annotations

import json

import pytest

from mcp_sweden.data.skolverket import FEATURE_META
from mcp_sweden.data.skolverket.tools import (
    get_school_detail,
    get_school_statistics,
    list_municipalities,
    list_school_forms,
    search_schools,
)


def test_feature_meta() -> None:
    """Verify feature metadata is correctly configured."""
    assert FEATURE_META.name == "skolverket"
    assert not FEATURE_META.requires_auth
    assert "education" in FEATURE_META.tags


@pytest.mark.asyncio
async def test_list_municipalities() -> None:
    """List municipalities returns valid data."""
    result = json.loads(await list_municipalities())
    assert result["count"] > 200  # Sweden has 290 municipalities
    first = result["municipalities"][0]
    assert "Kommunkod" in first
    assert "Namn" in first


@pytest.mark.asyncio
async def test_list_school_forms() -> None:
    """List school forms returns expected types."""
    result = json.loads(await list_school_forms())
    assert result["count"] > 5
    names = [sf["Benamning"] for sf in result["school_forms"]]
    assert "Grundskola" in names


@pytest.mark.asyncio
async def test_search_schools() -> None:
    """Search schools in Stockholm returns results."""
    result = json.loads(await search_schools(municipality_code="0180", size=5))
    assert len(result["school_units"]) > 0
    first = result["school_units"][0]
    assert "code" in first
    assert "name" in first
    assert first["geographicalAreaCode"] == "0180"


@pytest.mark.asyncio
async def test_search_schools_by_type() -> None:
    """Search gymnasium schools returns only gymnasium."""
    result = json.loads(await search_schools(type_of_schooling="gy", size=5))
    units = result["school_units"]
    assert len(units) > 0
    for unit in units:
        codes = [t["code"] for t in unit["typeOfSchooling"]]
        assert "gy" in codes


@pytest.mark.asyncio
async def test_get_school_detail() -> None:
    """Get detail for a known school unit."""
    result = json.loads(await get_school_detail("44673074"))
    assert result["code"] == "44673074"
    assert "name" in result
    assert "contactInfo" in result


@pytest.mark.asyncio
async def test_get_school_statistics() -> None:
    """Get statistics for a known school."""
    # First without type — should return available links
    result = json.loads(await get_school_statistics("44673074"))
    assert "_links" in result

    # Then with type gr (grundskola)
    stats = json.loads(await get_school_statistics("44673074", schooling_type="gr"))
    assert "schoolUnit" in stats or "studentsPerTeacherQuota" in stats
