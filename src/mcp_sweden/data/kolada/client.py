"""HTTP client for the Kolada API.

API base: https://api.kolada.se/v2
Docs: https://github.com/Hypergene/api

Key endpoints:
    - KPIs: GET /v2/kpi?title={query}
    - Municipalities: GET /v2/municipality?title={query}
    - Data: GET /v2/data/kpi/{kpi_id}/municipality/{municipality_id}/year/{year}
    - OU data: GET /v2/oudata/kpi/{kpi_id}/ou/{ou_id}/year/{year}
"""

from __future__ import annotations

from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

API_BASE = "https://api.kolada.se/v2"


@ttl_cache(ttl=600)
async def search_kpis(title: str = "", page: int = 1, per_page: int = 20) -> dict[str, Any]:
    """Search KPIs by title keyword."""
    params: dict[str, Any] = {"page": page, "per_page": per_page}
    if title:
        params["title"] = title
    return await http_get(f"{API_BASE}/kpi", params=params)


@ttl_cache(ttl=3600)
async def get_kpi(kpi_id: str) -> dict[str, Any]:
    """Get details for a specific KPI by ID."""
    return await http_get(f"{API_BASE}/kpi/{kpi_id}")


@ttl_cache(ttl=3600)
async def list_municipalities(title: str = "", type_filter: str = "") -> dict[str, Any]:
    """List municipalities or regions, optionally filtered by title."""
    params: dict[str, Any] = {}
    if title:
        params["title"] = title
    url = f"{API_BASE}/municipality"
    if type_filter:
        url = f"{API_BASE}/municipality?type={type_filter}"
    return await http_get(url, params=params if not type_filter else None)


@ttl_cache(ttl=3600)
async def get_municipality(municipality_id: str) -> dict[str, Any]:
    """Get details for a specific municipality."""
    return await http_get(f"{API_BASE}/municipality/{municipality_id}")


@ttl_cache(ttl=300)
async def get_data(
    kpi_id: str,
    municipality_id: str,
    year: int | None = None,
) -> dict[str, Any]:
    """Get KPI data for a municipality, optionally for a specific year."""
    url = f"{API_BASE}/data/kpi/{kpi_id}/municipality/{municipality_id}"
    if year:
        url += f"/year/{year}"
    return await http_get(url)


@ttl_cache(ttl=300)
async def get_data_multi(
    kpi_ids: str,
    municipality_ids: str,
    years: str,
) -> dict[str, Any]:
    """Get KPI data for multiple KPIs/municipalities/years.

    Args:
        kpi_ids: Comma-separated KPI IDs (e.g. "N00945,N00941")
        municipality_ids: Comma-separated municipality IDs (e.g. "0180,1480")
        years: Comma-separated years (e.g. "2020,2021,2022")
    """
    url = f"{API_BASE}/data/kpi/{kpi_ids}/municipality/{municipality_ids}/year/{years}"
    return await http_get(url)


@ttl_cache(ttl=600)
async def search_kpi_groups(title: str = "") -> dict[str, Any]:
    """Search KPI groups (thematic collections of KPIs)."""
    params: dict[str, Any] = {}
    if title:
        params["title"] = title
    return await http_get(f"{API_BASE}/kpi_groups", params=params)
