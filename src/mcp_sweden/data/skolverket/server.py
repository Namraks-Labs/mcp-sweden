"""Skolverket feature server — registers tools for Swedish education data.

Two APIs:
    - School Registry (skolenhetsregistret/v1): school details, municipalities
    - Planned Educations (planned-educations/v3): listings, statistics
"""

from fastmcp import FastMCP

from .tools import (
    find_schools_in_municipality,
    get_school_detail,
    get_school_registry_detail,
    get_school_statistics,
    list_municipalities,
    list_school_forms,
    search_schools,
)

mcp = FastMCP("mcp-sweden-skolverket")

# Reference data
mcp.tool(list_municipalities, tags={"reference", "municipalities"})
mcp.tool(list_school_forms, tags={"reference", "school-forms"})

# School search & details
mcp.tool(search_schools, tags={"schools", "search"})
mcp.tool(get_school_detail, tags={"schools", "detail"})
mcp.tool(get_school_registry_detail, tags={"schools", "registry", "detail"})
mcp.tool(find_schools_in_municipality, tags={"schools", "registry", "municipalities"})

# Statistics
mcp.tool(get_school_statistics, tags={"statistics", "schools"})
