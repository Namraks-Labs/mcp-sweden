"""Tool implementations for the SCB feature.

Each function becomes an MCP tool registered in server.py.
Tools provide a clean interface for LLMs to query Swedish statistics.
"""

from __future__ import annotations

from . import client


async def scb_list_subjects() -> str:
    """List all top-level subject areas in the SCB statistical database.

    Returns the root categories of Swedish official statistics, such as
    Population, Labor Market, Economy, Education, Environment, etc.

    Use this as a starting point to explore available statistics.
    """
    nodes = await client.list_subject_areas()

    if not nodes:
        return "No subject areas found."

    lines = ["SCB Subject Areas (top-level categories):", ""]
    for node in nodes:
        node_type = "folder" if node.type == "l" else "table"
        lines.append(f"  {node.id}: {node.text} [{node_type}]")

    lines.append("")
    lines.append("Use scb_browse with a subject code (e.g. 'BE' for Population) to explore.")
    return "\n".join(lines)


async def scb_browse(path: str) -> str:
    """Browse the SCB table hierarchy at a given path.

    Navigate deeper into the statistical database to find specific tables.

    Args:
        path: Hierarchy path, e.g. "BE" for Population,
              "BE/BE0101" for Population Statistics,
              "BE/BE0101/BE0101A" for specific sub-category.

    Returns:
        List of folders and tables at the given path.
    """
    nodes = await client.navigate(path)

    if not nodes:
        return f"No items found at path '{path}'. Check the path is correct."

    lines = [f"Contents of /{path}:", ""]
    tables = []
    folders = []

    for node in nodes:
        if node.type == "t":
            updated = f" (updated: {node.updated})" if node.updated else ""
            tables.append(f"  [TABLE] {node.id}: {node.text}{updated}")
        else:
            folders.append(f"  [DIR]   {node.id}: {node.text}")

    if folders:
        lines.append("Folders:")
        lines.extend(folders)
        lines.append("")

    if tables:
        lines.append("Tables:")
        lines.extend(tables)
        lines.append("")

    if tables:
        lines.append("Use scb_table_info with the full path (e.g. path + '/' + table_id) "
                      "to see variables and available values.")
    if folders:
        lines.append("Use scb_browse with a deeper path to explore further.")

    return "\n".join(lines)


async def scb_table_info(table_path: str) -> str:
    """Get metadata for a specific SCB table, including available variables.

    Shows the table title, all dimensions (variables), and their possible values.
    Use this to understand what data is available and how to query it.

    Args:
        table_path: Full path to the table,
                    e.g. "BE/BE0101/BE0101A/BesijObslAr".

    Returns:
        Table description with variables, value counts, and sample values.
    """
    metadata = await client.get_table_metadata(table_path)

    if not metadata.title and not metadata.variables:
        return (f"No metadata found for '{table_path}'. "
                "This might be a folder — use scb_browse instead.")

    lines = [f"Table: {metadata.title}", f"Path: {table_path}", ""]
    lines.append("Variables:")

    for var in metadata.variables:
        is_time = " [TIME]" if var.time else ""
        eliminable = " [optional]" if var.elimination else ""
        n_values = len(var.values)

        lines.append(f"  {var.code}: {var.text}{is_time}{eliminable}")
        lines.append(f"    {n_values} values available")

        # Show first few values as examples
        max_show = min(8, n_values)
        sample_pairs = []
        for i in range(max_show):
            code = var.values[i] if i < len(var.values) else "?"
            text = var.valueTexts[i] if i < len(var.valueTexts) else "?"
            sample_pairs.append(f"{code}={text}")

        lines.append(f"    Examples: {', '.join(sample_pairs)}")
        if n_values > max_show:
            lines.append(f"    ... and {n_values - max_show} more")
        lines.append("")

    lines.append("Use scb_query to fetch data. Provide selections as a JSON object")
    lines.append("mapping variable codes to lists of value codes.")
    return "\n".join(lines)


async def scb_query(
    table_path: str,
    selections: dict[str, list[str]] | None = None,
    latest_n: int | None = None,
    max_rows: int = 50,
) -> str:
    """Query data from an SCB statistics table.

    Fetches actual statistical data from the SCB database.

    Args:
        table_path: Full path to the table,
                    e.g. "BE/BE0101/BE0101A/BefolkningNy".
        selections: Optional dict mapping variable codes to value code lists.
                    Example: {"Region": ["00"], "Kon": ["1", "2"]}
                    If omitted, SCB returns data with default selections.
        latest_n: If set, automatically selects the N most recent time periods.
                  Useful for getting current data without knowing exact years.
        max_rows: Maximum rows to return (default 50). SCB can return thousands
                  of rows — this limits output for readability.

    Returns:
        Formatted table of results with column headers and data rows.
    """
    response = await client.query_table(
        table_path,
        selections=selections,
        top_n=latest_n,
    )

    if not response.columns and not response.data:
        return (f"No data returned for '{table_path}'. "
                "Check the path and selections. Use scb_table_info to see "
                "available variables and values.")

    # Build header
    col_names = [c.text for c in response.columns]
    lines = [" | ".join(col_names), "-" * (len(" | ".join(col_names)))]

    # Add data rows
    total_rows = len(response.data)
    display_rows = response.data[:max_rows]

    for row in display_rows:
        values = row.key + row.values
        lines.append(" | ".join(values))

    result_lines = [f"Results from: {table_path}", f"Total rows: {total_rows}", ""]
    result_lines.extend(lines)

    if total_rows > max_rows:
        result_lines.append(f"\n... showing {max_rows} of {total_rows} rows. "
                            "Narrow your selections to see fewer results.")

    # Add any comments
    if response.comments:
        result_lines.append("\nNotes:")
        for comment in response.comments:
            for key, val in comment.items():
                result_lines.append(f"  {key}: {val}")

    return "\n".join(result_lines)


async def scb_search(keyword: str, subject_area: str = "") -> str:
    """Search for SCB tables matching a keyword.

    Searches through the SCB hierarchy for tables whose names contain
    the given keyword. Useful when you know what topic you want but
    not the exact table path.

    Args:
        keyword: Search term (case-insensitive), e.g. "befolkning",
                 "population", "BNP", "unemployment".
        subject_area: Optional subject area code to narrow the search,
                      e.g. "BE" for population, "AM" for labor market.

    Returns:
        List of matching tables with their paths.
    """
    if not keyword or len(keyword) < 2:
        return "Please provide a search keyword with at least 2 characters."

    results = await client.search_tables(keyword, path=subject_area)

    if not results:
        msg = f"No tables found matching '{keyword}'"
        if subject_area:
            msg += f" in subject area '{subject_area}'"
        msg += ". Try a different keyword or broader search."
        return msg

    lines = [f"Search results for '{keyword}':", ""]
    for r in results:
        icon = "TABLE" if r["type"] == "table" else "DIR"
        updated = f" (updated: {r['updated']})" if r.get("updated") else ""
        lines.append(f"  [{icon}] /{r['path']}: {r['text']}{updated}")

    lines.append("")
    lines.append("For tables: use scb_table_info with the path to see variables.")
    lines.append("For folders: use scb_browse with the path to explore contents.")
    return "\n".join(lines)
