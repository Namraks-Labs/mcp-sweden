"""Riksdag feature server — registers tools for Swedish Parliament data.

API docs: https://data.riksdagen.se/
Available endpoints: documents, members, votes, speeches/debates.
"""

from fastmcp import FastMCP

from .tools import (
    get_member_details,
    list_members,
    search_documents,
    search_speeches,
    search_votes,
)

mcp = FastMCP("mcp-sweden-riksdag")

mcp.tool(search_documents, tags={"documents", "legislation", "parliament"})
mcp.tool(list_members, tags={"members", "parliament"})
mcp.tool(get_member_details, tags={"members", "parliament"})
mcp.tool(search_votes, tags={"votes", "decisions", "parliament"})
mcp.tool(search_speeches, tags={"speeches", "debates", "parliament"})
