"""Riksdag feature server — registers tools for Swedish Parliament data.

API docs: https://data.riksdagen.se/
Available endpoints: documents, members, votes, debates, committees.
"""

from fastmcp import FastMCP

mcp = FastMCP("mcp-sweden-riksdag")

# TODO: Register tools here after implementation
# Example:
# from .tools import search_documents, list_members, get_votes
# mcp.tool(search_documents, tags={"documents", "legislation"})
# mcp.tool(list_members, tags={"members", "parliament"})
# mcp.tool(get_votes, tags={"votes", "decisions"})
