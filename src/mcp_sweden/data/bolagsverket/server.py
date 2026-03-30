"""Bolagsverket feature server — registers tools for Swedish company registry data.

Provides MCP tools for searching and looking up companies registered
with Bolagsverket (Swedish Companies Registration Office).

API docs: https://foretagsregistret.bolagsverket.se/
"""

from fastmcp import FastMCP

from .tools import (
    get_company_events,
    get_company_info,
    get_company_officers,
    search_companies,
)

mcp = FastMCP("mcp-sweden-bolagsverket")

mcp.tool(search_companies, tags={"companies", "search"})
mcp.tool(get_company_info, tags={"companies", "details"})
mcp.tool(get_company_officers, tags={"companies", "officers", "board"})
mcp.tool(get_company_events, tags={"companies", "events", "registration"})
