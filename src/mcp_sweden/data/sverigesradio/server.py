"""Sveriges Radio feature server — registers tools for Swedish public radio.

API docs: https://sverigesradio.se/oppetapi
"""

from fastmcp import FastMCP

from .tools import (
    get_episodes,
    get_latest_episode,
    get_now_playing,
    get_playlist,
    get_schedule,
    get_traffic_messages,
    list_channels,
    list_traffic_areas,
    search_programs,
)

mcp = FastMCP("mcp-sweden-sverigesradio")

# Channels & Schedule
mcp.tool(list_channels, tags={"channels", "radio", "discovery"})
mcp.tool(get_schedule, tags={"schedule", "broadcast", "channels"})

# Programs & Episodes
mcp.tool(search_programs, tags={"programs", "search", "discovery"})
mcp.tool(get_episodes, tags={"episodes", "programs", "audio"})
mcp.tool(get_latest_episode, tags={"episodes", "programs", "latest"})

# Playlists / Now Playing
mcp.tool(get_playlist, tags={"playlist", "music", "songs"})
mcp.tool(get_now_playing, tags={"nowplaying", "live", "channels"})

# Traffic
mcp.tool(get_traffic_messages, tags={"traffic", "incidents", "roads"})
mcp.tool(list_traffic_areas, tags={"traffic", "areas", "geography"})
