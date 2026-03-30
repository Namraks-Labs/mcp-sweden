"""Tool implementations for the Begagnad feature.

Each function becomes an MCP tool registered in server.py.
"""

from __future__ import annotations

import json
from typing import Any

from . import client


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Blocket
# ---------------------------------------------------------------------------


async def search_blocket(query: str, limit: int = 20) -> str:
    """Search Blocket for second-hand items in Sweden.

    Blocket is Sweden's largest classifieds marketplace. Search for anything
    from furniture and electronics to vehicles and housing.

    Args:
        query: Search term (e.g. "IKEA soffa", "iPhone 15", "cykel Stockholm").
        limit: Maximum number of results (default: 20).

    Returns:
        JSON with matching listings including title, price, location,
        condition, seller info, and images.
    """
    items = await client.search_blocket(query, limit=limit)
    if not items:
        return f'No Blocket listings found for "{query}".'

    return _json({"count": len(items), "source": "blocket", "items": items})


async def get_blocket_item(ad_id: str) -> str:
    """Get full details of a specific Blocket listing.

    Use search_blocket first to find ad IDs, then use this tool for
    complete details including full description and all images.

    Args:
        ad_id: The Blocket ad ID (from search results).

    Returns:
        JSON with full listing details.
    """
    item = await client.get_blocket_item(ad_id)
    return _json(item)


# ---------------------------------------------------------------------------
# Tradera
# ---------------------------------------------------------------------------


async def search_tradera(query: str, page: int = 1) -> str:
    """Search Tradera auctions and buy-it-now listings in Sweden.

    Tradera is Sweden's largest auction site (owned by PayPal/eBay).
    Requires TRADERA_APP_ID and TRADERA_APP_KEY environment variables.

    Args:
        query: Search term (e.g. "vintage klocka", "Nintendo Switch",
               "retro möbler").
        page: Page number for pagination (default: 1).

    Returns:
        JSON with matching auction/listing items including title, current
        price/bid, seller info, end date, and images. Returns empty if
        Tradera credentials are not configured.
    """
    if not client.is_tradera_available():
        return (
            "Tradera search unavailable — set TRADERA_APP_ID and "
            "TRADERA_APP_KEY environment variables. "
            "Register at https://api.tradera.com to get free credentials."
        )

    items = await client.search_tradera(query, page=page)
    if not items:
        return f'No Tradera listings found for "{query}".'

    return _json({"count": len(items), "source": "tradera", "page": page, "items": items})


async def get_tradera_item(item_id: str) -> str:
    """Get full details of a specific Tradera listing.

    Use search_tradera first to find item IDs, then use this tool for
    complete details including full description and bid history.
    Requires TRADERA_APP_ID and TRADERA_APP_KEY.

    Args:
        item_id: The Tradera item ID (from search results).

    Returns:
        JSON with full listing details.
    """
    if not client.is_tradera_available():
        return "Tradera unavailable — set TRADERA_APP_ID and TRADERA_APP_KEY environment variables."

    item = await client.get_tradera_item(item_id)
    return _json(item)


# ---------------------------------------------------------------------------
# Combined search
# ---------------------------------------------------------------------------


async def search_begagnad(query: str, blocket_limit: int = 20) -> str:
    """Search both Blocket and Tradera simultaneously for second-hand items.

    This is the recommended tool for general searches — it queries both
    Swedish marketplaces at once and returns unified results. Tradera results
    are only included if credentials are configured.

    Args:
        query: Search term (e.g. "begagnad laptop", "barnkläder",
               "PlayStation 5").
        blocket_limit: Maximum Blocket results (default: 20).

    Returns:
        JSON with combined results from both marketplaces, with source
        indicated per item. Includes counts per marketplace.
    """
    blocket_items = await client.search_blocket(query, limit=blocket_limit)

    tradera_items: list[dict[str, Any]] = []
    tradera_note = ""
    if client.is_tradera_available():
        tradera_items = await client.search_tradera(query)
    else:
        tradera_note = "Tradera skipped (credentials not configured)"

    all_items = blocket_items + tradera_items
    if not all_items:
        return f'No second-hand listings found for "{query}".'

    result: dict[str, Any] = {
        "total": len(all_items),
        "blocket_count": len(blocket_items),
        "tradera_count": len(tradera_items),
        "items": all_items,
    }
    if tradera_note:
        result["note"] = tradera_note

    return _json(result)
