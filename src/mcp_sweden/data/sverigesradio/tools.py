"""Tool implementations for the Sveriges Radio feature.

Each function becomes an MCP tool registered in server.py.
"""

from __future__ import annotations

import json
from typing import Any

from . import client


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Channels & Schedule
# ---------------------------------------------------------------------------


async def list_channels() -> str:
    """List all Sveriges Radio channels (P1, P2, P3, P4 regional, etc.).

    Returns channel IDs, names, taglines, and live audio stream URLs.
    Use the channel ID with other tools to get schedules, playlists, etc.
    """
    data = await client.list_channels(size=100)
    channels = data.get("channels", [])
    if not channels:
        return "No channels found."

    results = []
    for ch in channels:
        entry: dict[str, Any] = {
            "id": ch.get("id"),
            "name": ch.get("name", ""),
            "tagline": ch.get("tagline", ""),
            "channel_type": ch.get("channeltype", ""),
        }
        live_audio = ch.get("liveaudio", {})
        if live_audio and live_audio.get("url"):
            entry["live_audio_url"] = live_audio["url"]
        results.append(entry)

    return _json({"count": len(results), "channels": results})


async def get_schedule(
    channel_id: int,
    date: str = "",
    page: int = 1,
    size: int = 20,
) -> str:
    """Get the broadcast schedule for a Sveriges Radio channel.

    Shows what programs are airing and when on a given day.

    Args:
        channel_id: SR channel ID (e.g. 132 for P1, 163 for P2, 164 for P3).
                    Use list_channels to find IDs.
        date: Date in YYYY-MM-DD format. Leave empty for today's schedule.
        page: Page number for pagination (default: 1).
        size: Results per page (default: 20).

    Returns:
        JSON with scheduled episodes including title, description,
        start/end times, and program info.
    """
    data = await client.get_schedule(channel_id, date=date, page=page, size=size)
    episodes = data.get("schedule", [])
    if not episodes:
        return f"No schedule found for channel {channel_id}" + (
            f" on {date}." if date else " today."
        )

    results = []
    for ep in episodes:
        entry: dict[str, Any] = {
            "title": ep.get("title", ""),
            "description": ep.get("description", ""),
            "start_time": ep.get("starttimeutc", ""),
            "end_time": ep.get("endtimeutc", ""),
        }
        program = ep.get("program", {})
        if program:
            entry["program_id"] = program.get("id")
            entry["program_name"] = program.get("name", "")
        results.append(entry)

    pagination = data.get("pagination", {})
    return _json(
        {
            "channel_id": channel_id,
            "date": date or "today",
            "total": pagination.get("totalhits", len(results)),
            "page": pagination.get("page", page),
            "schedule": results,
        }
    )


# ---------------------------------------------------------------------------
# Programs & Episodes
# ---------------------------------------------------------------------------


async def search_programs(
    query: str = "",
    channel_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> str:
    """Search Sveriges Radio programs by name or browse by channel.

    Args:
        query: Search term to filter programs (e.g. "Ekot", "Vetenskapsradion",
               "Sommar"). Leave empty to browse all.
        channel_id: Filter to a specific channel ID. Leave empty for all channels.
        page: Page number (default: 1).
        size: Results per page (default: 20).

    Returns:
        JSON with matching programs including ID, name, description,
        and which channel they air on.
    """
    if query:
        data = await client.search_programs(query, page=page, size=size)
    else:
        data = await client.list_programs(channel_id=channel_id, page=page, size=size)

    programs = data.get("programs", [])
    if not programs:
        msg = f"No programs found matching '{query}'." if query else "No programs found."
        return msg

    results = []
    for p in programs:
        entry: dict[str, Any] = {
            "id": p.get("id"),
            "name": p.get("name", ""),
            "description": p.get("description", ""),
            "program_category": p.get("programcategory", {}).get("name", ""),
            "channel": p.get("channel", {}).get("name", ""),
            "channel_id": p.get("channel", {}).get("id"),
        }
        if p.get("programurl"):
            entry["url"] = p["programurl"]
        results.append(entry)

    pagination = data.get("pagination", {})
    return _json(
        {
            "total": pagination.get("totalhits", len(results)),
            "page": pagination.get("page", page),
            "programs": results,
        }
    )


async def get_episodes(
    program_id: int,
    page: int = 1,
    size: int = 10,
) -> str:
    """Get episodes for a Sveriges Radio program.

    Args:
        program_id: Program ID (find with search_programs).
        page: Page number (default: 1).
        size: Results per page (default: 10).

    Returns:
        JSON with episodes including title, description, publish date,
        and audio download URL where available.
    """
    data = await client.list_episodes(program_id, page=page, size=size)
    episodes = data.get("episodes", [])
    if not episodes:
        return f"No episodes found for program {program_id}."

    results = []
    for ep in episodes:
        entry: dict[str, Any] = {
            "id": ep.get("id"),
            "title": ep.get("title", ""),
            "description": ep.get("description", ""),
            "publish_date": ep.get("publishdateutc", ""),
        }
        broadcast = ep.get("broadcast", {})
        if broadcast:
            entry["broadcast_start"] = broadcast.get("broadcaststartutc", "")
            entry["broadcast_end"] = broadcast.get("broadcastendutc", "")
        audio = ep.get("downloadpodfile", {}) or ep.get("listenpodfile", {})
        if audio and audio.get("url"):
            entry["audio_url"] = audio["url"]
            entry["audio_duration"] = audio.get("duration", 0)
        results.append(entry)

    pagination = data.get("pagination", {})
    return _json(
        {
            "program_id": program_id,
            "total": pagination.get("totalhits", len(results)),
            "page": pagination.get("page", page),
            "episodes": results,
        }
    )


async def get_latest_episode(program_id: int) -> str:
    """Get the most recent episode of a Sveriges Radio program.

    Useful for quickly checking what was last broadcast.

    Args:
        program_id: Program ID (find with search_programs).

    Returns:
        JSON with the latest episode details and audio URL.
    """
    data = await client.get_latest_episode(program_id)
    ep = data.get("episode")
    if not ep:
        return f"No latest episode found for program {program_id}."

    entry: dict[str, Any] = {
        "id": ep.get("id"),
        "title": ep.get("title", ""),
        "description": ep.get("description", ""),
        "publish_date": ep.get("publishdateutc", ""),
        "program": ep.get("program", {}).get("name", ""),
    }
    audio = ep.get("downloadpodfile", {}) or ep.get("listenpodfile", {})
    if audio and audio.get("url"):
        entry["audio_url"] = audio["url"]
        entry["audio_duration"] = audio.get("duration", 0)

    return _json(entry)


# ---------------------------------------------------------------------------
# Playlists / Now Playing
# ---------------------------------------------------------------------------


async def get_playlist(channel_id: int, size: int = 10) -> str:
    """Get recently played songs on a Sveriges Radio music channel.

    Args:
        channel_id: Channel ID (e.g. 164 for P3). Use list_channels to find IDs.
        size: Number of recent songs to return (default: 10).

    Returns:
        JSON with recently played songs including artist, title, and play time.
    """
    data = await client.get_playlist(channel_id, size=size)
    songs = data.get("song", [])
    if not songs:
        return f"No playlist data found for channel {channel_id}."

    results = []
    for s in songs:
        results.append(
            {
                "title": s.get("title", ""),
                "artist": s.get("artist", ""),
                "album": s.get("albumname", ""),
                "start_time": s.get("starttimeutc", ""),
                "stop_time": s.get("stoptimeutc", ""),
            }
        )

    return _json({"channel_id": channel_id, "songs": results})


async def get_now_playing(channel_id: int) -> str:
    """Get what is playing right now on a Sveriges Radio channel.

    Shows the current song and previous song (if music channel).

    Args:
        channel_id: Channel ID (e.g. 132 for P1, 164 for P3).

    Returns:
        JSON with currently playing song and channel information.
    """
    data = await client.get_now_playing(channel_id)
    playlist = data.get("playlist", {})
    if not playlist:
        return f"No now-playing data for channel {channel_id}."

    channel_info = playlist.get("channel", {})
    result: dict[str, Any] = {
        "channel": channel_info.get("name", ""),
        "channel_id": channel_info.get("id", channel_id),
    }

    current_song = playlist.get("song", {})
    if current_song and current_song.get("title"):
        result["current_song"] = {
            "title": current_song.get("title", ""),
            "artist": current_song.get("artist", ""),
            "album": current_song.get("albumname", ""),
            "start_time": current_song.get("starttimeutc", ""),
        }

    previous_song = playlist.get("previoussong", {})
    if previous_song and previous_song.get("title"):
        result["previous_song"] = {
            "title": previous_song.get("title", ""),
            "artist": previous_song.get("artist", ""),
        }

    next_song = playlist.get("nextsong", {})
    if next_song and next_song.get("title"):
        result["next_song"] = {
            "title": next_song.get("title", ""),
            "artist": next_song.get("artist", ""),
        }

    return _json(result)


# ---------------------------------------------------------------------------
# Traffic
# ---------------------------------------------------------------------------


async def get_traffic_messages(
    area: str = "",
    page: int = 1,
    size: int = 20,
) -> str:
    """Get current traffic messages from Sveriges Radio's traffic service.

    Covers road incidents, closures, delays, and warnings across Sweden.

    Args:
        area: Traffic area name (e.g. "Stockholm", "Göteborg", "Skåne").
              Leave empty for nationwide messages.
        page: Page number (default: 1).
        size: Results per page (default: 20).

    Returns:
        JSON with traffic messages including location, category,
        severity (priority), and description.
    """
    data = await client.get_traffic_messages(traffic_area=area, page=page, size=size)
    messages = data.get("messages", [])
    if not messages:
        if area:
            return f"No traffic messages for area '{area}'."
        return "No traffic messages right now."

    results = []
    for m in messages:
        entry: dict[str, Any] = {
            "title": m.get("title", ""),
            "description": m.get("description", ""),
            "category": m.get("category", ""),
            "subcategory": m.get("subcategory", ""),
            "priority": m.get("priority", 0),
            "exact_location": m.get("exactlocation", ""),
            "created": m.get("createddate", ""),
        }
        area_info = m.get("area", "")
        if area_info:
            entry["area"] = area_info
        results.append(entry)

    pagination = data.get("pagination", {})
    return _json(
        {
            "area": area or "nationwide",
            "total": pagination.get("totalhits", len(results)),
            "page": pagination.get("page", page),
            "messages": results,
        }
    )


async def list_traffic_areas() -> str:
    """List all Swedish traffic areas used by Sveriges Radio.

    Use the area names with get_traffic_messages to filter by region.

    Returns:
        JSON with all traffic area names.
    """
    data = await client.list_traffic_areas()
    areas = data.get("areas", [])
    if not areas:
        return "No traffic areas found."

    results = [{"name": a.get("name", ""), "radius": a.get("radius", 0)} for a in areas]
    return _json({"count": len(results), "areas": results})
