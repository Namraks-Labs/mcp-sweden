"""Tool implementations for the Skolverket feature.

Provides MCP tools for querying Swedish school data via Skolverket's APIs.
"""

from __future__ import annotations

import json
from typing import Any

from . import client


def _fmt(data: Any) -> str:
    """Format data as compact JSON."""
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


async def list_municipalities() -> str:
    """List all Swedish municipalities with their codes.

    Use municipality codes to filter school searches.
    Returns all 290 municipalities with name and code.
    """
    items = await client.list_municipalities()
    return _fmt({"count": len(items), "municipalities": items})


async def list_school_forms() -> str:
    """List all school form types in Sweden.

    Returns types like Grundskola, Gymnasieskola, Förskoleklass, etc.
    with their IDs and codes for use in filtering.
    """
    items = await client.list_school_forms()
    return _fmt({"count": len(items), "school_forms": items})


async def search_schools(
    municipality_code: str | None = None,
    type_of_schooling: str | None = None,
    page: int = 0,
    size: int = 20,
) -> str:
    """Search for schools across Sweden.

    Filter by municipality and/or type of schooling.
    Returns school names, codes, locations, and education types offered.

    Args:
        municipality_code: Municipality code (e.g. "0180" for Stockholm).
            Use list_municipalities to find codes.
        type_of_schooling: Filter by schooling type code:
            gr = Grundskola, gy = Gymnasieskola, fsk = Förskoleklass,
            gran = Anpassad grundskola, gyan = Anpassad gymnasieskola.
        page: Page number (0-indexed). Default 0.
        size: Results per page (1-100). Default 20.
    """
    result = await client.search_school_units_planned(
        municipality_code=municipality_code,
        type_of_schooling=type_of_schooling,
        page=page,
        size=min(size, 100),
    )
    return _fmt(result)


async def get_school_detail(school_code: str) -> str:
    """Get detailed information about a specific school.

    Returns contact info, address, coordinates, education types,
    principal organizer, and more.

    Args:
        school_code: The school unit code (e.g. "44673074").
            Find codes via search_schools.
    """
    detail = await client.get_school_unit_planned(school_code)
    return _fmt(detail)


async def get_school_registry_detail(school_code: str) -> str:
    """Get comprehensive registry information about a school.

    Returns rector name, email, phone, website, full address with
    geo coordinates, school forms with year ranges, and principal
    organizer details.

    Args:
        school_code: The school unit code (e.g. "44673074").
    """
    detail = await client.get_school_unit_detail(school_code)
    return _fmt(detail)


async def get_school_statistics(
    school_code: str,
    schooling_type: str | None = None,
) -> str:
    """Get statistics for a school — teacher ratios, certified teachers, etc.

    Returns time series data with values across multiple school years.
    Statistics include students-per-teacher ratio, certified teacher
    percentage, special educator ratios, and more.

    Args:
        school_code: The school unit code (e.g. "44673074").
        schooling_type: Schooling type code (gr, gy, fsk, gran, gyan).
            If omitted, returns links to available statistic types.
    """
    stats = await client.get_school_unit_statistics(school_code, schooling_type)
    return _fmt(stats)


async def find_schools_in_municipality(municipality_code: str) -> str:
    """Find all schools registered in a municipality via the school registry.

    Returns a comprehensive list with school codes, names, org numbers,
    and active/inactive status. Useful for getting an overview of all
    educational institutions in an area.

    Args:
        municipality_code: Municipality code (e.g. "0180" for Stockholm).
            Use list_municipalities to find codes.
    """
    items = await client.search_school_units_registry(municipality_code)
    active = [s for s in items if s.get("Status") == "Aktiv"]
    return _fmt({
        "municipality_code": municipality_code,
        "total": len(items),
        "active": len(active),
        "schools": items[:100],  # Cap to avoid huge responses
    })
