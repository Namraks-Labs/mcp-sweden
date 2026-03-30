"""HTTP client for the Sveriges Radio API.

API base: https://api.sr.se/api/v2
Docs: https://sverigesradio.se/oppetapi

All endpoints accept ``format=json`` to return JSON instead of XML.
Paginated endpoints use ``page`` and ``size`` parameters.
"""

from __future__ import annotations

from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

API_BASE = "https://api.sr.se/api/v2"

# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------


@ttl_cache(ttl=3600)
async def list_channels(page: int = 1, size: int = 30) -> dict[str, Any]:
    """List all Sveriges Radio channels."""
    return await http_get(
        f"{API_BASE}/channels",
        params={"format": "json", "page": page, "size": size},
    )


@ttl_cache(ttl=3600)
async def get_channel(channel_id: int) -> dict[str, Any]:
    """Get details for a specific channel."""
    return await http_get(
        f"{API_BASE}/channels/{channel_id}",
        params={"format": "json"},
    )


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------


@ttl_cache(ttl=300)
async def get_schedule(
    channel_id: int,
    date: str = "",
    page: int = 1,
    size: int = 30,
) -> dict[str, Any]:
    """Get the broadcast schedule for a channel.

    Args:
        channel_id: SR channel ID (e.g. 132 for P1).
        date: Date in YYYY-MM-DD format. Empty for today.
        page: Page number.
        size: Results per page.
    """
    params: dict[str, Any] = {"format": "json", "page": page, "size": size}
    if date:
        params["date"] = date
    return await http_get(
        f"{API_BASE}/scheduledepisodes",
        params={"channelid": channel_id, **params},
    )


# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------


@ttl_cache(ttl=600)
async def list_programs(
    channel_id: int | None = None,
    page: int = 1,
    size: int = 30,
) -> dict[str, Any]:
    """List programs, optionally filtered by channel."""
    params: dict[str, Any] = {"format": "json", "page": page, "size": size}
    if channel_id is not None:
        params["channelid"] = channel_id
    return await http_get(f"{API_BASE}/programs/index", params=params)


@ttl_cache(ttl=600)
async def search_programs(query: str, page: int = 1, size: int = 30) -> dict[str, Any]:
    """Search programs by name."""
    return await http_get(
        f"{API_BASE}/programs/index",
        params={"format": "json", "page": page, "size": size, "filter": query},
    )


@ttl_cache(ttl=3600)
async def get_program(program_id: int) -> dict[str, Any]:
    """Get details for a specific program."""
    return await http_get(
        f"{API_BASE}/programs/{program_id}",
        params={"format": "json"},
    )


# ---------------------------------------------------------------------------
# Episodes
# ---------------------------------------------------------------------------


@ttl_cache(ttl=300)
async def list_episodes(
    program_id: int,
    page: int = 1,
    size: int = 10,
) -> dict[str, Any]:
    """List episodes for a program."""
    return await http_get(
        f"{API_BASE}/episodes/index",
        params={"programid": program_id, "format": "json", "page": page, "size": size},
    )


@ttl_cache(ttl=3600)
async def get_episode(episode_id: int) -> dict[str, Any]:
    """Get details for a specific episode."""
    return await http_get(
        f"{API_BASE}/episodes/get",
        params={"id": episode_id, "format": "json"},
    )


@ttl_cache(ttl=300)
async def get_latest_episode(program_id: int) -> dict[str, Any]:
    """Get the latest episode for a program."""
    return await http_get(
        f"{API_BASE}/episodes/getlatest",
        params={"programid": program_id, "format": "json"},
    )


# ---------------------------------------------------------------------------
# Playlists / Now Playing
# ---------------------------------------------------------------------------


@ttl_cache(ttl=60)
async def get_playlist(channel_id: int, size: int = 10) -> dict[str, Any]:
    """Get recent playlist (songs played) for a channel."""
    return await http_get(
        f"{API_BASE}/playlists/getplaylistbychannelid",
        params={"id": channel_id, "format": "json", "size": size},
    )


@ttl_cache(ttl=30)
async def get_now_playing(channel_id: int) -> dict[str, Any]:
    """Get the currently playing song on a channel."""
    return await http_get(
        f"{API_BASE}/playlists/rightnow",
        params={"channelid": channel_id, "format": "json"},
    )


# ---------------------------------------------------------------------------
# News (Ekot)
# ---------------------------------------------------------------------------


@ttl_cache(ttl=120)
async def get_news(program_id: int = 4540, page: int = 1, size: int = 10) -> dict[str, Any]:
    """Get latest news episodes (default: Ekot, program 4540)."""
    return await http_get(
        f"{API_BASE}/episodes/index",
        params={"programid": program_id, "format": "json", "page": page, "size": size},
    )


# ---------------------------------------------------------------------------
# Traffic
# ---------------------------------------------------------------------------


@ttl_cache(ttl=120)
async def get_traffic_messages(
    traffic_area: str = "",
    page: int = 1,
    size: int = 20,
) -> dict[str, Any]:
    """Get current traffic messages from SR's traffic service.

    Args:
        traffic_area: Traffic area name (e.g. "Stockholm", "Göteborg").
                      Empty for nationwide.
        page: Page number.
        size: Results per page.
    """
    params: dict[str, Any] = {"format": "json", "page": page, "size": size}
    if traffic_area:
        params["trafficareaname"] = traffic_area
    return await http_get(f"{API_BASE}/traffic/messages", params=params)


@ttl_cache(ttl=3600)
async def list_traffic_areas() -> dict[str, Any]:
    """List all traffic areas in Sweden."""
    return await http_get(
        f"{API_BASE}/traffic/areas",
        params={"format": "json"},
    )
