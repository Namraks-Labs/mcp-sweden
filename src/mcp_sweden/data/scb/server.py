"""SCB feature server — registers tools for Statistics Sweden data.

API docs: https://www.scb.se/vara-tjanster/oppna-data/api-for-statistikdatabasen/
The SCB API uses a POST-based query model with JSON table specifications.
"""

from fastmcp import FastMCP

mcp = FastMCP("mcp-sweden-scb")

# TODO: Register tools here after implementation
# Example:
# from .tools import list_tables, query_table, search_statistics
# mcp.tool(list_tables, tags={"tables", "catalog"})
# mcp.tool(query_table, tags={"query", "data"})
