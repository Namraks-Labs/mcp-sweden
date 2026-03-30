"""HTTP clients for Swedish second-hand marketplace APIs.

Blocket API (no auth required):
    - Search: GET https://blocket-api.se/v1/custom-search
    - Item:   GET https://blocket-api.se/v1/get-ad-by-id

Tradera API (requires TRADERA_APP_ID + TRADERA_APP_KEY):
    - Search: GET https://api.tradera.com/v3/searchservice.asmx/Search
    - Item:   GET https://api.tradera.com/v3/publicservice.asmx/GetItem
    Note: Tradera returns XML, parsed to dict.
"""

from __future__ import annotations

import os
import re
from typing import Any
from xml.etree import ElementTree

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import create_client
from mcp_sweden.exceptions import HttpClientError

BLOCKET_API = "https://blocket-api.se/v1"
TRADERA_API = "https://api.tradera.com/v3"


# ---------------------------------------------------------------------------
# Blocket
# ---------------------------------------------------------------------------


@ttl_cache(ttl=120)
async def search_blocket(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search Blocket listings."""
    async with create_client() as client:
        resp = await client.get(
            f"{BLOCKET_API}/custom-search",
            params={"query": query, "limit": limit},
        )
        if resp.status_code >= 400:
            raise HttpClientError(f"{BLOCKET_API}/custom-search", resp.status_code)
        data = resp.json()

    items = data.get("data", [])
    if not isinstance(items, list):
        return []

    results: list[dict[str, Any]] = []
    for item in items:
        price_obj = item.get("price", {})
        location_list = item.get("location", [])
        advertiser = item.get("advertiser", {})

        # Extract condition from parameter groups
        condition = None
        for group in item.get("parameter_groups", []):
            if group.get("type") == "general":
                for param in group.get("parameters", []):
                    if param.get("id") == "item_condition":
                        condition = param.get("short_value")
                        break

        results.append({
            "id": str(item.get("ad_id", item.get("list_id", ""))),
            "title": item.get("subject", ""),
            "description": item.get("body", ""),
            "price": price_obj.get("value") if isinstance(price_obj, dict) else None,
            "currency": "SEK",
            "location": location_list[0].get("name", "") if location_list else "",
            "url": item.get("share_url", ""),
            "images": [
                img.get("url", "") for img in item.get("images", []) if img.get("url")
            ],
            "condition": condition,
            "seller_name": advertiser.get("name", ""),
            "seller_rating": (
                advertiser.get("public_profile", {}).get("reviews", {}).get("overall_score")
            ),
            "end_date": item.get("list_time"),
            "source": "blocket",
        })
    return results


@ttl_cache(ttl=300)
async def get_blocket_item(ad_id: str) -> dict[str, Any]:
    """Get a single Blocket listing by ad ID."""
    async with create_client() as client:
        resp = await client.get(
            f"{BLOCKET_API}/get-ad-by-id",
            params={"ad_id": ad_id},
        )
        if resp.status_code >= 400:
            raise HttpClientError(f"{BLOCKET_API}/get-ad-by-id", resp.status_code)
        data = resp.json()

    item = data.get("data")
    if not item:
        raise HttpClientError(f"{BLOCKET_API}/get-ad-by-id", detail=f"Item not found: {ad_id}")

    price_obj = item.get("price", {})
    location_list = item.get("location", [])
    advertiser = item.get("advertiser", {})

    condition = None
    for group in item.get("parameter_groups", []):
        if group.get("type") == "general":
            for param in group.get("parameters", []):
                if param.get("id") == "item_condition":
                    condition = param.get("short_value")
                    break

    return {
        "id": str(item.get("ad_id", item.get("list_id", ""))),
        "title": item.get("subject", ""),
        "description": item.get("body", ""),
        "price": price_obj.get("value") if isinstance(price_obj, dict) else None,
        "currency": "SEK",
        "location": location_list[0].get("name", "") if location_list else "",
        "url": item.get("share_url", ""),
        "images": [
            img.get("url", "") for img in item.get("images", []) if img.get("url")
        ],
        "condition": condition,
        "seller_name": advertiser.get("name", ""),
        "seller_rating": (
            advertiser.get("public_profile", {}).get("reviews", {}).get("overall_score")
        ),
        "end_date": item.get("list_time"),
        "source": "blocket",
    }


# ---------------------------------------------------------------------------
# Tradera
# ---------------------------------------------------------------------------


def _tradera_credentials() -> tuple[str, str] | None:
    """Return (app_id, app_key) or None if not configured."""
    app_id = os.environ.get("TRADERA_APP_ID", "")
    app_key = os.environ.get("TRADERA_APP_KEY", "")
    if app_id and app_key:
        return app_id, app_key
    return None


def _parse_xml_to_dict(xml_text: str) -> dict[str, Any]:
    """Parse Tradera XML response into a simplified dict.

    Strips namespace prefixes for cleaner access.
    """
    # Strip XML namespaces for easier parsing
    clean = re.sub(r'\sxmlns[^"]*"[^"]*"', "", xml_text)
    clean = re.sub(r"<(/?)[\w]+:", r"<\1", clean)

    root = ElementTree.fromstring(clean)
    result = _element_to_dict(root)
    return result if isinstance(result, dict) else {}


def _element_to_dict(element: ElementTree.Element) -> dict[str, Any] | str:
    """Recursively convert an XML element to a dict."""
    result: dict[str, Any] = {}

    for child in element:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        child_data = _element_to_dict(child)

        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(child_data)
        else:
            result[tag] = child_data

    text = (element.text or "").strip()
    if not result and text:
        return text
    if text:
        result["_text"] = text
    return result


@ttl_cache(ttl=120)
async def search_tradera(query: str, page: int = 1) -> list[dict[str, Any]]:
    """Search Tradera auctions. Requires TRADERA_APP_ID and TRADERA_APP_KEY."""
    creds = _tradera_credentials()
    if creds is None:
        return []

    app_id, app_key = creds
    async with create_client() as client:
        resp = await client.get(
            f"{TRADERA_API}/searchservice.asmx/Search",
            params={
                "query": query,
                "categoryId": 0,
                "pageNumber": page,
                "orderBy": "Relevance",
                "appId": app_id,
                "appKey": app_key,
            },
        )
        if resp.status_code >= 400:
            raise HttpClientError(
                f"{TRADERA_API}/searchservice.asmx/Search", resp.status_code
            )

    parsed = _parse_xml_to_dict(resp.text)
    items_raw = parsed.get("Items", {})
    if isinstance(items_raw, str):
        return []

    items = items_raw.get("Item", [])
    if isinstance(items, dict):
        items = [items]

    results: list[dict[str, Any]] = []
    for item in items:
        # Extract image URLs
        image_links = item.get("ImageLinks", {})
        if isinstance(image_links, dict):
            image_list = image_links.get("ImageLink", [])
            if isinstance(image_list, dict):
                image_list = [image_list]
        else:
            image_list = []

        images = [
            link.get("Url", "")
            for link in image_list
            if isinstance(link, dict) and link.get("Format") == "normal" and link.get("Url")
        ]

        price = (
            item.get("BuyItNowPrice")
            or item.get("MaxBid")
            or item.get("NextBid")
        )

        results.append({
            "id": str(item.get("Id", "")),
            "title": item.get("ShortDescription", ""),
            "description": item.get("LongDescription", ""),
            "price": float(price) if price else None,
            "currency": "SEK",
            "location": "",
            "url": item.get("ItemUrl", ""),
            "images": images,
            "condition": None,
            "seller_name": item.get("SellerAlias", ""),
            "seller_rating": (
                float(item["SellerDsrAverage"])
                if item.get("SellerDsrAverage")
                else None
            ),
            "end_date": item.get("EndDate"),
            "source": "tradera",
            "item_type": item.get("ItemType"),
        })
    return results


@ttl_cache(ttl=300)
async def get_tradera_item(item_id: str) -> dict[str, Any]:
    """Get a single Tradera item by ID. Requires credentials."""
    creds = _tradera_credentials()
    if creds is None:
        raise HttpClientError(
            f"{TRADERA_API}/publicservice.asmx/GetItem",
            detail="TRADERA_APP_ID and TRADERA_APP_KEY not set",
        )

    app_id, app_key = creds
    async with create_client() as client:
        resp = await client.get(
            f"{TRADERA_API}/publicservice.asmx/GetItem",
            params={
                "itemId": item_id,
                "appId": app_id,
                "appKey": app_key,
            },
        )
        if resp.status_code >= 400:
            raise HttpClientError(
                f"{TRADERA_API}/publicservice.asmx/GetItem", resp.status_code
            )

    parsed = _parse_xml_to_dict(resp.text)
    item = parsed if parsed else {}

    if not item or not item.get("Id"):
        raise HttpClientError(
            f"{TRADERA_API}/publicservice.asmx/GetItem",
            detail=f"Item not found: {item_id}",
        )

    # Extract images
    image_links = item.get("DetailedImageLinks", {})
    if isinstance(image_links, dict):
        image_list = image_links.get("ImageLink", [])
        if isinstance(image_list, dict):
            image_list = [image_list]
    else:
        image_list = []

    images = [
        link.get("Url", "")
        for link in image_list
        if isinstance(link, dict) and link.get("Url")
    ]

    seller = item.get("Seller", {})
    if isinstance(seller, str):
        seller = {}

    price = item.get("MaxBid") or item.get("NextBid") or item.get("BuyItNowPrice")

    return {
        "id": str(item.get("Id", "")),
        "title": item.get("ShortDescription", ""),
        "description": (item.get("LongDescription", "") or "")
        .replace("<br>", "\n")
        .replace("&lt;", "<")
        .replace("&gt;", ">"),
        "price": float(price) if price else None,
        "currency": "SEK",
        "location": seller.get("City", ""),
        "url": item.get("ItemLink", ""),
        "images": images,
        "condition": None,
        "seller_name": seller.get("Alias", ""),
        "seller_rating": (
            float(seller["TotalRating"]) if seller.get("TotalRating") else None
        ),
        "end_date": item.get("EndDate"),
        "source": "tradera",
        "item_type": item.get("ItemType"),
    }


def is_tradera_available() -> bool:
    """Check if Tradera credentials are configured."""
    return _tradera_credentials() is not None
