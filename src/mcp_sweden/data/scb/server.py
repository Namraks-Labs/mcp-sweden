"""SCB feature server — registers tools for Statistics Sweden data.

API docs: https://www.scb.se/vara-tjanster/oppna-data/api-for-statistikdatabasen/
The SCB API uses a POST-based query model with JSON table specifications.

Tools:
    - scb_list_subjects: List top-level subject areas
    - scb_browse: Navigate the table hierarchy
    - scb_table_info: Get table metadata and variables
    - scb_query: Query statistical data
    - scb_search: Search for tables by keyword
"""

from fastmcp import FastMCP

from .tools import scb_browse, scb_list_subjects, scb_query, scb_search, scb_table_info

mcp = FastMCP("mcp-sweden-scb")

mcp.tool(scb_list_subjects, tags={"catalog", "navigation"})
mcp.tool(scb_browse, tags={"catalog", "navigation"})
mcp.tool(scb_table_info, tags={"metadata", "tables"})
mcp.tool(scb_query, tags={"query", "data", "statistics"})
mcp.tool(scb_search, tags={"search", "discovery"})
