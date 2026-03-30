"""HTTP client for the Riksdag API.

API base: https://data.riksdagen.se
Documentation: https://data.riksdagen.se/dokumentation/

Key endpoints:
    - Documents: GET /dokumentlista/
    - Members: GET /personlista/
    - Votes: GET /voteringlista/
    - Speeches: GET /anforandelista/
"""

from __future__ import annotations

import logging
from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get

logger = logging.getLogger(__name__)

API_BASE = "https://data.riksdagen.se"


async def _get_json(path: str, params: dict[str, Any] | None = None) -> Any:
    """Fetch JSON from the Riksdag API."""
    url = f"{API_BASE}{path}"
    all_params: dict[str, Any] = {"utformat": "json"}
    if params:
        all_params.update(params)
    return await http_get(url, params=all_params)


async def search_documents(
    query: str = "",
    doc_type: str = "",
    session: str = "",
    organ: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Search parliament documents.

    Args:
        query: Free text search.
        doc_type: Document type filter (e.g. 'mot' for motions, 'prop' for propositions).
        session: Parliamentary session (e.g. '2024/25').
        organ: Committee/organ code (e.g. 'FiU' for Finance Committee).
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (1-based).
        page_size: Results per page (max 200).
    """
    params: dict[str, Any] = {
        "sok": query,
        "doktyp": doc_type,
        "rm": session,
        "organ": organ,
        "from": from_date,
        "tom": to_date,
        "p": page,
        "sz": min(page_size, 200),
    }
    # Remove empty values
    params = {k: v for k, v in params.items() if v}
    return await _get_json("/dokumentlista/", params)


@ttl_cache(ttl=600)
async def list_members(
    party: str = "",
    constituency: str = "",
    status: str = "",
) -> dict[str, Any]:
    """List parliament members.

    Args:
        party: Party abbreviation filter (e.g. 'S', 'M', 'SD').
        constituency: Constituency filter (e.g. 'Stockholms kommun').
        status: Status filter — empty for current members.
    """
    params: dict[str, Any] = {
        "parti": party,
        "valkrets": constituency,
        "status": status,
    }
    params = {k: v for k, v in params.items() if v}
    return await _get_json("/personlista/", params)


async def get_member(person_id: str) -> dict[str, Any]:
    """Get detailed info about a specific parliament member."""
    return await _get_json(f"/person/{person_id}/json")


async def search_votes(
    session: str = "",
    designation: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Search parliamentary votes.

    Args:
        session: Parliamentary session (e.g. '2024/25').
        designation: Vote designation (e.g. '2024/25:FiU10').
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (1-based).
        page_size: Results per page.
    """
    params: dict[str, Any] = {
        "rm": session,
        "bet": designation,
        "from": from_date,
        "tom": to_date,
        "p": page,
        "sz": min(page_size, 200),
    }
    params = {k: v for k, v in params.items() if v}
    return await _get_json("/voteringlista/", params)


async def search_speeches(
    query: str = "",
    party: str = "",
    person_id: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    """Search parliamentary speeches/debates.

    Args:
        query: Free text search in speech content.
        party: Filter by party abbreviation.
        person_id: Filter by speaker's person ID.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (1-based).
        page_size: Results per page.
    """
    params: dict[str, Any] = {
        "sok": query,
        "parti": party,
        "intressent_id": person_id,
        "from": from_date,
        "tom": to_date,
        "p": page,
        "sz": min(page_size, 200),
    }
    params = {k: v for k, v in params.items() if v}
    return await _get_json("/anforandelista/", params)
