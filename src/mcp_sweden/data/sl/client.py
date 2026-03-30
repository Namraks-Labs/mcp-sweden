"""HTTP client for the SL Transport API.

API base: https://transport.integration.sl.se/v1
No authentication required.

Key endpoints:
    - Sites: GET /sites
    - Departures: GET /sites/{id}/departures
    - Lines: GET /lines?transport_authority_id=1
"""

from __future__ import annotations

import logging
import math
from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

logger = logging.getLogger(__name__)

API_BASE = "https://transport.integration.sl.se/v1"

# Transport authority ID for SL (Storstockholms Lokaltrafik)
SL_TRANSPORT_AUTHORITY_ID = 1

# Valid transport modes
TRANSPORT_MODES = ("METRO", "BUS", "TRAM", "TRAIN", "SHIP", "FERRY", "TAXI")


async def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch from the SL Transport API."""
    url = f"{API_BASE}{path}"
    return await http_get(url, params=params)


@ttl_cache(ttl=600)
async def list_sites() -> list[dict[str, Any]]:
    """Fetch all SL sites/stations.

    Returns a list of ~6,500 sites with id, name, coordinates.
    Cached for 10 minutes since station data rarely changes.
    """
    result = await _get("/sites")
    if isinstance(result, list):
        return result
    return []


async def search_sites(query: str) -> list[dict[str, Any]]:
    """Search sites by name (case-insensitive substring match).

    The API doesn't support server-side filtering, so we fetch all
    and filter locally. Results are cached via list_sites().
    """
    sites = await list_sites()
    q = query.lower()
    return [s for s in sites if q in s.get("name", "").lower()]


async def get_nearby_sites(lat: float, lon: float, radius_km: float = 1.0) -> list[dict[str, Any]]:
    """Find sites near a given coordinate.

    Uses the Haversine formula to calculate distance.
    """
    sites = await list_sites()
    results: list[dict[str, Any]] = []

    for site in sites:
        site_lat = site.get("lat")
        site_lon = site.get("lon")
        if site_lat is None or site_lon is None:
            continue

        dist = _haversine(lat, lon, site_lat, site_lon)
        if dist <= radius_km:
            results.append({**site, "_distance_km": round(dist, 2)})

    results.sort(key=lambda s: s["_distance_km"])
    return results


async def get_departures(
    site_id: int,
    transport_mode: str = "",
    direction: int = 0,
    line: str = "",
) -> dict[str, Any]:
    """Get real-time departures from a specific site.

    Args:
        site_id: The site/station ID.
        transport_mode: Filter by mode (METRO, BUS, TRAM, TRAIN, SHIP, FERRY).
        direction: Direction code (1 or 2). 0 = both directions.
        line: Filter by line designation (e.g. '10', '172').
    """
    params: dict[str, Any] = {}
    if transport_mode and transport_mode.upper() in TRANSPORT_MODES:
        params["transport_mode"] = transport_mode.upper()
    if direction in (1, 2):
        params["direction"] = direction
    if line:
        params["line"] = line

    result = await _get(f"/sites/{site_id}/departures", params=params or None)
    if isinstance(result, dict):
        return result
    return {}


@ttl_cache(ttl=3600)
async def list_lines() -> dict[str, list[dict[str, Any]]]:
    """Fetch all SL lines grouped by transport mode.

    Returns a dict with keys: metro, tram, train, bus, ship, ferry, taxi.
    Cached for 1 hour since line data rarely changes.
    """
    result = await _get(f"/lines?transport_authority_id={SL_TRANSPORT_AUTHORITY_ID}")
    if isinstance(result, dict):
        return result
    return {}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in km."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
