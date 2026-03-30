"""Kolada feature server — registers tools for municipality & region stats.

API docs: https://github.com/Hypergene/api
"""

from fastmcp import FastMCP

from .tools import (
    compare_municipalities,
    get_kpi_data,
    get_kpi_details,
    search_kpi_groups,
    search_kpis,
    search_municipalities,
)

mcp = FastMCP("mcp-sweden-kolada")

mcp.tool(search_kpis, tags={"kpi", "search", "indicators"})
mcp.tool(get_kpi_details, tags={"kpi", "metadata"})
mcp.tool(search_municipalities, tags={"municipalities", "regions", "search"})
mcp.tool(get_kpi_data, tags={"kpi", "data", "statistics"})
mcp.tool(compare_municipalities, tags={"kpi", "comparison", "ranking"})
mcp.tool(search_kpi_groups, tags={"kpi", "groups", "discovery"})
