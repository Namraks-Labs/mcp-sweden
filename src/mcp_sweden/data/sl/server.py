"""SL feature server — registers tools for Stockholm public transport.

API docs: https://www.trafiklab.se/api/trafiklab-apis/sl/transport/
No authentication required.
"""

from fastmcp import FastMCP

from .tools import (
    get_departures,
    get_nearby_stations,
    get_station_info,
    list_lines,
    search_stations,
)

mcp = FastMCP("mcp-sweden-sl")

mcp.tool(search_stations, tags={"stations", "search", "transport"})
mcp.tool(get_departures, tags={"departures", "realtime", "transport"})
mcp.tool(list_lines, tags={"lines", "transport"})
mcp.tool(get_station_info, tags={"stations", "info", "transport"})
mcp.tool(get_nearby_stations, tags={"stations", "nearby", "geo", "transport"})
