"""Tool implementations for the Kolada feature.

Each function becomes an MCP tool registered in server.py.
"""

from __future__ import annotations

import json

from . import client


async def search_kpis(query: str = "", page: int = 1, per_page: int = 20) -> str:
    """Search Kolada KPIs (Key Performance Indicators) by keyword.

    Kolada contains thousands of KPIs covering education, health, economy,
    environment, demographics, and more for all Swedish municipalities and regions.

    Args:
        query: Search term to filter KPIs by title (e.g. "befolkning", "skola", "vård").
               Leave empty to browse all KPIs.
        page: Page number for pagination (default: 1).
        per_page: Results per page, max 100 (default: 20).

    Returns:
        JSON with matching KPIs including ID, title, and description.
        Use the KPI ID with get_kpi_data to retrieve actual values.
    """
    data = await client.search_kpis(title=query, page=page, per_page=per_page)
    values = data.get("values", [])
    count = data.get("count", 0)

    if not values:
        return f"No KPIs found matching '{query}'." if query else "No KPIs found."

    results = []
    for kpi in values:
        entry = {
            "id": kpi.get("id", ""),
            "title": kpi.get("title", ""),
            "description": kpi.get("description", ""),
        }
        if kpi.get("operating_area"):
            entry["operating_area"] = kpi["operating_area"]
        results.append(entry)

    return json.dumps(
        {"total_count": count, "page": page, "kpis": results},
        ensure_ascii=False,
        indent=2,
    )


async def get_kpi_details(kpi_id: str) -> str:
    """Get detailed information about a specific Kolada KPI.

    Args:
        kpi_id: The KPI identifier (e.g. "N00945" for population growth).

    Returns:
        Full KPI metadata including title, description, operating area,
        whether it has gender-split data, and publication dates.
    """
    data = await client.get_kpi(kpi_id)
    values = data.get("values", [])

    if not values:
        return f"KPI '{kpi_id}' not found."

    kpi = values[0]
    return json.dumps(
        {
            "id": kpi.get("id", ""),
            "title": kpi.get("title", ""),
            "description": kpi.get("description", ""),
            "operating_area": kpi.get("operating_area", ""),
            "has_ou_data": kpi.get("has_ou_data", False),
            "is_divided_by_gender": kpi.get("is_divided_by_gender", 0),
            "municipality_type": kpi.get("municipality_type", ""),
            "publication_date": kpi.get("publication_date", ""),
        },
        ensure_ascii=False,
        indent=2,
    )


async def search_municipalities(
    query: str = "",
    type_filter: str = "",
) -> str:
    """Search Swedish municipalities and regions.

    Sweden has 290 municipalities (kommun) and 21 regions (landsting/region).

    Args:
        query: Search term to filter by name (e.g. "Stockholm", "Göteborg").
               Leave empty to list all.
        type_filter: Filter by type: "K" for municipalities, "L" for regions.
                     Leave empty for both.

    Returns:
        JSON list of matching municipalities/regions with ID, name, and type.
        Use the municipality ID with get_kpi_data to retrieve statistics.
    """
    data = await client.list_municipalities(title=query, type_filter=type_filter)
    values = data.get("values", [])

    if not values:
        if query:
            return f"No municipalities found matching '{query}'."
        return "No municipalities found."

    results = []
    for m in values:
        raw_type = m.get("type", "")
        if raw_type == "K":
            mtype = "municipality"
        elif raw_type == "L":
            mtype = "region"
        else:
            mtype = raw_type
        results.append({
            "id": m.get("id", ""),
            "title": m.get("title", ""),
            "type": mtype,
        })

    return json.dumps(
        {"count": len(results), "municipalities": results},
        ensure_ascii=False,
        indent=2,
    )


async def get_kpi_data(
    kpi_id: str,
    municipality_id: str,
    year: int | None = None,
) -> str:
    """Get KPI data values for a specific municipality or region.

    Retrieves actual statistical values for a KPI in a given municipality.

    Args:
        kpi_id: KPI identifier (e.g. "N00945"). Find IDs with search_kpis.
        municipality_id: Municipality/region ID (e.g. "0180" for Stockholm).
                         Find IDs with search_municipalities.
        year: Specific year to query (e.g. 2023). Omit for all available years.

    Returns:
        JSON with data values grouped by period, including gender breakdowns
        where available.
    """
    data = await client.get_data(kpi_id, municipality_id, year)
    values = data.get("values", [])

    if not values:
        return f"No data found for KPI {kpi_id} in municipality {municipality_id}."

    results = []
    for period_data in values:
        period = period_data.get("period", "")
        period_values = period_data.get("values", [])
        for v in period_values:
            entry: dict[str, str | float | None] = {
                "period": period,
                "value": v.get("value"),
                "gender": v.get("gender", "T"),
            }
            if v.get("status"):
                entry["status"] = v["status"]
            results.append(entry)

    return json.dumps(
        {"kpi": kpi_id, "municipality": municipality_id, "data": results},
        ensure_ascii=False,
        indent=2,
    )


async def compare_municipalities(
    kpi_id: str,
    municipality_ids: str,
    years: str = "2023",
) -> str:
    """Compare KPI values across multiple municipalities or regions.

    Useful for benchmarking and ranking Swedish municipalities on any indicator.

    Args:
        kpi_id: KPI identifier (e.g. "N00945").
        municipality_ids: Comma-separated municipality IDs (e.g. "0180,1480,1280"
                          for Stockholm, Göteborg, Malmö).
        years: Comma-separated years (e.g. "2021,2022,2023"). Default: "2023".

    Returns:
        JSON comparison table with values for each municipality and year.
    """
    data = await client.get_data_multi(kpi_id, municipality_ids, years)
    values = data.get("values", [])

    if not values:
        return f"No comparison data found for KPI {kpi_id}."

    results = []
    for period_data in values:
        period = period_data.get("period", "")
        for v in period_data.get("values", []):
            results.append({
                "period": period,
                "municipality": v.get("municipality", ""),
                "value": v.get("value"),
                "gender": v.get("gender", "T"),
            })

    return json.dumps(
        {"kpi": kpi_id, "comparison": results},
        ensure_ascii=False,
        indent=2,
    )


async def search_kpi_groups(query: str = "") -> str:
    """Search thematic groups of KPIs in Kolada.

    KPI groups organize related indicators by theme (e.g. education,
    healthcare, economy). Useful for discovering what data is available.

    Args:
        query: Search term to filter groups by title. Leave empty to browse all.

    Returns:
        JSON list of KPI groups with their member KPIs.
    """
    data = await client.search_kpi_groups(title=query)
    values = data.get("values", [])

    if not values:
        return f"No KPI groups found matching '{query}'." if query else "No KPI groups found."

    results = []
    for group in values:
        entry: dict[str, str | list[str]] = {
            "id": group.get("id", ""),
            "title": group.get("title", ""),
        }
        members = group.get("members", [])
        if members:
            entry["member_kpis"] = [m.get("member_id", "") for m in members[:10]]
            if len(members) > 10:
                entry["total_members"] = str(len(members))
        results.append(entry)

    return json.dumps(
        {"count": len(results), "groups": results},
        ensure_ascii=False,
        indent=2,
    )
