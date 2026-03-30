"""Tool implementations for the Bolagsverket feature.

Each async function becomes an MCP tool registered in server.py.
Tools provide access to Swedish company registry data from Bolagsverket.
"""

from __future__ import annotations

from . import client


async def search_companies(
    query: str,
    page: int = 1,
) -> str:
    """Search Swedish company registry by name or organization number.

    Query can be a company name (e.g. "Spotify"), a partial name,
    or an organization number (e.g. "5560123456" or "556012-3456").

    Args:
        query: Company name or organization number to search for.
        page: Page number for pagination (default 1).

    Returns:
        Formatted list of matching companies with org numbers and types.
    """
    result = await client.search_companies(query=query, page=page)
    return result.format()


async def get_company_info(org_number: str) -> str:
    """Get detailed information about a Swedish company by organization number.

    Returns registration details, address, business activity,
    share capital, and employee count.

    Args:
        org_number: Swedish organization number (10 digits, e.g. "5560123456" or "556012-3456").

    Returns:
        Formatted company details or error message.
    """
    company = await client.get_company(org_number)
    if company is None:
        formatted = client._format_org_number(org_number)
        return f"Company not found: {formatted}"
    return company.format()


async def get_company_officers(org_number: str) -> str:
    """Get board members and officers for a Swedish company.

    Returns the current board of directors, CEO, auditors,
    and other registered officers.

    Args:
        org_number: Swedish organization number (10 digits).

    Returns:
        Formatted list of company officers with roles.
    """
    officers = await client.get_company_officers(org_number)
    if not officers:
        formatted = client._format_org_number(org_number)
        return f"No officers found for {formatted}."

    formatted = client._format_org_number(org_number)
    header = f"Officers for {formatted}:\n"
    items = [o.format() for o in officers]
    return header + "\n".join(items)


async def get_company_events(org_number: str) -> str:
    """Get registration events and changes for a Swedish company.

    Returns a chronological list of registration changes such as
    board changes, address updates, name changes, and filings.

    Args:
        org_number: Swedish organization number (10 digits).

    Returns:
        Formatted list of registration events.
    """
    events = await client.get_company_events(org_number)
    if not events:
        formatted = client._format_org_number(org_number)
        return f"No registration events found for {formatted}."

    formatted = client._format_org_number(org_number)
    header = f"Registration events for {formatted}:\n"
    items = [e.format() for e in events]
    return header + "\n".join(items)
