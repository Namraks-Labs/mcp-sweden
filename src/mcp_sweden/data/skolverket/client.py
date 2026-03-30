"""HTTP client for the Skolverket APIs.

Two APIs are used:
    1. School Registry (skolenhetsregistret/v1) — school unit details, municipalities
    2. Planned Educations (planned-educations/v3) — school listings, statistics
"""

from __future__ import annotations

from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

# --- Base URLs ---
REGISTRY_BASE = "https://api.skolverket.se/skolenhetsregistret/v1"
PLANNED_BASE = "https://api.skolverket.se/planned-educations/v3"

# The planned-educations API requires a vendor-specific Accept header
_PLANNED_HEADERS = {
    "Accept": "application/vnd.skolverket.plannededucations.api.v3.hal+json",
}


# ---------------------------------------------------------------------------
# School Registry API (skolenhetsregistret/v1)
# ---------------------------------------------------------------------------


@ttl_cache(ttl=3600)
async def list_municipalities() -> list[dict[str, Any]]:
    """List all Swedish municipalities with codes."""
    data = await http_get(f"{REGISTRY_BASE}/kommun")
    return data.get("Kommuner", [])  # type: ignore[no-any-return]


@ttl_cache(ttl=3600)
async def list_school_forms() -> list[dict[str, Any]]:
    """List all school form types (grundskola, gymnasium, etc.)."""
    data = await http_get(f"{REGISTRY_BASE}/skolform")
    return data.get("Skolformer", [])  # type: ignore[no-any-return]


async def search_school_units_registry(
    municipality_code: str | None = None,
) -> list[dict[str, Any]]:
    """Search school units from the registry. Optionally filter by municipality."""
    params: dict[str, str] = {}
    if municipality_code:
        params["kommun"] = municipality_code
    data = await http_get(f"{REGISTRY_BASE}/skolenhet", params=params or None)
    return data.get("Skolenheter", [])  # type: ignore[no-any-return]


async def get_school_unit_detail(school_code: str) -> dict[str, Any]:
    """Get detailed info for a specific school unit from the registry."""
    data = await http_get(f"{REGISTRY_BASE}/skolenhet/{school_code}")
    return data.get("SkolenhetInfo", data)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Planned Educations API (planned-educations/v3)
# ---------------------------------------------------------------------------


async def search_school_units_planned(
    municipality_code: str | None = None,
    type_of_schooling: str | None = None,
    page: int = 0,
    size: int = 20,
) -> dict[str, Any]:
    """Search school units via the planned-educations API.

    Args:
        municipality_code: Filter by municipality (geographicalAreaCode).
        type_of_schooling: Filter by type code (gr, gy, fsk, gran, etc.).
        page: Page number (0-indexed).
        size: Results per page (max ~100).

    Returns:
        Dict with 'school_units' list and 'page' metadata.
    """
    params: dict[str, Any] = {"page": page, "size": size}
    if municipality_code:
        params["geographicalAreaCode"] = municipality_code
    if type_of_schooling:
        params["typeOfSchooling"] = type_of_schooling

    data = await http_get(
        f"{PLANNED_BASE}/school-units", params=params, headers=_PLANNED_HEADERS
    )
    body = data.get("body", {})
    embedded = body.get("_embedded", {})
    return {
        "school_units": embedded.get("listedSchoolUnits", []),
        "page": body.get("page", {}),
    }


async def get_school_unit_planned(school_code: str) -> dict[str, Any]:
    """Get school unit details from the planned-educations API."""
    data = await http_get(
        f"{PLANNED_BASE}/school-units/{school_code}", headers=_PLANNED_HEADERS
    )
    return data.get("body", data)  # type: ignore[no-any-return]


async def get_school_unit_statistics(
    school_code: str,
    schooling_type: str | None = None,
) -> dict[str, Any]:
    """Get statistics for a school unit.

    Args:
        school_code: The school unit code.
        schooling_type: Optional schooling type code (gr, gy, fsk, etc.).
            If omitted, returns available statistic links.

    Returns:
        Statistics dict with teacher ratios, certified teacher quotas, etc.
    """
    url = f"{PLANNED_BASE}/school-units/{school_code}/statistics"
    if schooling_type:
        url = f"{url}/{schooling_type}"
    data = await http_get(url, headers=_PLANNED_HEADERS)
    return data.get("body", data)  # type: ignore[no-any-return]
