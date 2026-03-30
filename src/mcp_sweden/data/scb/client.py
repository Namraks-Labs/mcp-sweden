"""HTTP client for the SCB API.

API base: https://api.scb.se/OV0104/v1/doris
Documentation: https://www.scb.se/vara-tjanster/oppna-data/api-for-statistikdatabasen/

Key endpoints:
    - Navigation: GET /sv/ssd/ (browse table hierarchy)
    - Table metadata: GET /sv/ssd/{table_id}
    - Query data: POST /sv/ssd/{table_id} (with JSON query body)

The SCB API is free, no auth required. Rate limit: ~10 req/s recommended.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get, http_post
from mcp_sweden._shared.rate_limiter import RateLimiter

from .schemas import (
    QueryRequest,
    QueryResponse,
    QueryVariable,
    ResponseColumn,
    ResponseRow,
    TableMetadata,
    TableNode,
    Variable,
    VariableSelection,
)

logger = logging.getLogger(__name__)

API_BASE = "https://api.scb.se/OV0104/v1/doris"

# SCB recommends max 10 requests per 10 seconds
_limiter = RateLimiter(max_calls=10, period=10.0)


@ttl_cache(ttl=600)
async def navigate(path: str = "") -> list[TableNode]:
    """Browse the SCB table hierarchy.

    Args:
        path: Hierarchy path (e.g. "" for root, "BE" for population,
              "BE/BE0101" for population statistics).

    Returns:
        List of child nodes (folders or tables).
    """
    url = f"{API_BASE}/sv/ssd/{path}" if path else f"{API_BASE}/sv/ssd"

    async with _limiter:
        raw = await http_get(url)

    if not isinstance(raw, list):
        return []

    return [TableNode(**item) for item in raw]


@ttl_cache(ttl=600)
async def get_table_metadata(table_path: str) -> TableMetadata:
    """Get metadata for a specific table, including its variables.

    Args:
        table_path: Full path to the table (e.g. "BE/BE0101/BE0101A/BesijObslAr").

    Returns:
        Table metadata with variable definitions.
    """
    url = f"{API_BASE}/sv/ssd/{table_path}"

    async with _limiter:
        raw = await http_get(url)

    if not isinstance(raw, dict):
        return TableMetadata()

    variables = []
    for var_data in raw.get("variables", []):
        variables.append(Variable(**var_data))

    return TableMetadata(
        title=raw.get("title", ""),
        variables=variables,
    )


async def query_table(
    table_path: str,
    selections: dict[str, list[str]] | None = None,
    top_n: int | None = None,
) -> QueryResponse:
    """Query data from an SCB table.

    Args:
        table_path: Full path to the table.
        selections: Dict mapping variable codes to lists of value codes.
            If None, queries with default/all values.
        top_n: If set, use "top" filter to get the N most recent values
            for the time variable (useful for getting latest data).

    Returns:
        Query response with columns and data rows.
    """
    url = f"{API_BASE}/sv/ssd/{table_path}"

    # Build query body
    query_vars: list[QueryVariable] = []

    if selections:
        for code, values in selections.items():
            query_vars.append(
                QueryVariable(
                    code=code,
                    selection=VariableSelection(filter="item", values=values),
                )
            )

    # If top_n is set, we need to know the time variable.
    # We'll get metadata first to find it.
    if top_n is not None:
        metadata = await get_table_metadata(table_path)
        time_var = next((v for v in metadata.variables if v.time), None)
        if time_var:
            # Check if time variable is already in selections
            existing_codes = {qv.code for qv in query_vars}
            if time_var.code not in existing_codes:
                query_vars.append(
                    QueryVariable(
                        code=time_var.code,
                        selection=VariableSelection(
                            filter="top", values=[str(top_n)]
                        ),
                    )
                )

    request = QueryRequest(query=query_vars)

    async with _limiter:
        raw = await http_post(url, json=request.model_dump())

    if not isinstance(raw, dict):
        return QueryResponse()

    columns = [ResponseColumn(**c) for c in raw.get("columns", [])]
    data_rows = [ResponseRow(**r) for r in raw.get("data", [])]
    comments = raw.get("comments", [])

    return QueryResponse(columns=columns, data=data_rows, comments=comments)


@ttl_cache(ttl=3600)
async def list_subject_areas() -> list[TableNode]:
    """List all top-level subject areas in the SCB database.

    These are the root categories like:
    - AM (Arbetsmarknad / Labor market)
    - BE (Befolkning / Population)
    - BO (Boende, byggnader / Housing)
    - EN (Energi / Energy)
    - etc.
    """
    return await navigate("")


async def search_tables(keyword: str, path: str = "") -> list[dict[str, Any]]:
    """Search for tables matching a keyword by traversing the hierarchy.

    This does a breadth-first search through the SCB hierarchy,
    looking for tables whose text contains the keyword.

    Args:
        keyword: Search term (case-insensitive).
        path: Starting path for search (default: root).

    Returns:
        List of matching tables with their paths.
    """
    keyword_lower = keyword.lower()
    results: list[dict[str, Any]] = []
    to_visit: list[str] = [path]
    visited: set[str] = set()
    max_results = 20
    max_depth = 3

    while to_visit and len(results) < max_results:
        current_path = to_visit.pop(0)

        if current_path in visited:
            continue
        visited.add(current_path)

        # Check depth
        depth = len(current_path.split("/")) if current_path else 0
        if depth > max_depth:
            continue

        nodes = await navigate(current_path)
        for node in nodes:
            node_path = f"{current_path}/{node.id}" if current_path else node.id

            if keyword_lower in node.text.lower():
                results.append(
                    {
                        "path": node_path,
                        "text": node.text,
                        "type": "table" if node.type == "t" else "folder",
                        "updated": node.updated,
                    }
                )

            # Queue folders for further exploration
            if node.type == "l" and len(results) < max_results:
                to_visit.append(node_path)

    return results[:max_results]
