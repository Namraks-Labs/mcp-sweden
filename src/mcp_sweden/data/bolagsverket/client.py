"""HTTP client for Bolagsverket (Swedish Companies Registration Office).

Uses the Bolagsverket Företagsregistret public search and lookup endpoints.

API base: https://foretagsregistret.bolagsverket.se
Key endpoints:
    - Search: POST /fir-search/api/search
    - Company: GET /fir-search/api/company/{org_number}

Note: These endpoints provide basic company registration data.
For full API access (annual reports, detailed financials), register
at https://bolagsverket.se/ for API credentials.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from mcp_sweden._shared.http_client import create_client
from mcp_sweden.exceptions import HttpClientError

from .schemas import (
    Company,
    CompanyAddress,
    CompanyEvent,
    CompanyOfficer,
    CompanySearchResult,
)

logger = logging.getLogger(__name__)

API_BASE = "https://foretagsregistret.bolagsverket.se"
SEARCH_ENDPOINT = "/fir-search/api/search"
COMPANY_ENDPOINT = "/fir-search/api/company"


def _normalize_org_number(org_number: str) -> str:
    """Normalize org number to 10 digits (remove dash if present)."""
    cleaned = re.sub(r"[^0-9]", "", org_number)
    if len(cleaned) == 12:
        cleaned = cleaned[2:]
    if len(cleaned) != 10:
        raise ValueError(
            f"Invalid org number '{org_number}': expected 10 digits, got {len(cleaned)}"
        )
    return cleaned


def _format_org_number(org_number: str) -> str:
    """Format org number as NNNNNN-NNNN."""
    cleaned = _normalize_org_number(org_number)
    return f"{cleaned[:6]}-{cleaned[6:]}"


def _parse_company(data: dict[str, Any]) -> Company:
    """Parse a company record from the API response."""
    address_data = data.get("address", {}) or {}
    address = CompanyAddress(
        street=address_data.get("street", "") or "",
        postal_code=address_data.get("postalCode", "") or address_data.get("zipCode", "") or "",
        city=address_data.get("city", "") or address_data.get("town", "") or "",
        municipality=address_data.get("municipality", "") or "",
        county=address_data.get("county", "") or "",
    )

    return Company(
        org_number=data.get("organisationNumber", "") or data.get("orgNumber", "") or "",
        name=data.get("name", "") or data.get("companyName", "") or "",
        company_type=data.get("companyForm", "") or data.get("type", "") or "",
        status=data.get("status", "") or data.get("registrationStatus", "") or "",
        registration_date=data.get("registrationDate", "") or "",
        address=address,
        business_description=data.get("businessDescription", "") or data.get("activity", "") or "",
        share_capital=data.get("shareCapital", "") or "",
        num_employees=data.get("numberOfEmployees", "") or data.get("employees", "") or "",
    )


def _parse_officer(data: dict[str, Any]) -> CompanyOfficer:
    """Parse an officer record."""
    return CompanyOfficer(
        name=data.get("name", "") or data.get("fullName", "") or "",
        role=data.get("role", "") or data.get("title", "") or "",
        personal_number_last4=data.get("personalNumberLast4", "") or "",
        appointed_date=data.get("appointedDate", "") or data.get("since", "") or "",
    )


def _parse_event(data: dict[str, Any]) -> CompanyEvent:
    """Parse a registration event."""
    return CompanyEvent(
        date=data.get("date", "") or data.get("eventDate", "") or "",
        event_type=data.get("type", "") or data.get("eventType", "") or "",
        description=data.get("description", "") or data.get("text", "") or "",
    )


async def search_companies(
    query: str,
    page: int = 1,
    page_size: int = 10,
) -> CompanySearchResult:
    """Search for companies by name or organization number.

    Args:
        query: Company name or org number to search for.
        page: Page number (1-based).
        page_size: Results per page (max 25).
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    digits_only = re.sub(r"[^0-9]", "", query)
    is_org_number = bool(re.match(r"^[\d\- ]+$", query.strip()) and len(digits_only) >= 6)

    params: dict[str, Any] = {
        "query": query.strip(),
        "offset": (page - 1) * page_size,
        "limit": min(page_size, 25),
    }

    try:
        async with create_client(base_url=API_BASE, headers=headers) as client:
            response = await client.post(SEARCH_ENDPOINT, json=params)

            if response.status_code == 200:
                data = response.json()
                hits = data.get("hits", data.get("results", data.get("companies", [])))
                total = data.get("totalHits", data.get("total", len(hits)))

                companies = [_parse_company(hit) for hit in hits] if isinstance(hits, list) else []

                return CompanySearchResult(
                    companies=companies,
                    total_count=total,
                    page=page,
                    query=query,
                )

            if response.status_code == 404 and is_org_number:
                company = await get_company(_normalize_org_number(query))
                if company:
                    return CompanySearchResult(
                        companies=[company],
                        total_count=1,
                        page=1,
                        query=query,
                    )

            logger.warning(
                "Search returned status %d for query '%s'",
                response.status_code,
                query,
            )
            return CompanySearchResult(query=query)

    except (HttpClientError, Exception) as exc:
        logger.error("Company search failed for '%s': %s", query, exc)
        return CompanySearchResult(query=query)


async def get_company(org_number: str) -> Company | None:
    """Get company details by organization number.

    Args:
        org_number: Swedish org number (10 digits, with or without dash).

    Returns:
        Company details or None if not found.
    """
    normalized = _normalize_org_number(org_number)
    formatted = _format_org_number(org_number)

    headers = {"Accept": "application/json"}

    try:
        async with create_client(base_url=API_BASE, headers=headers) as client:
            response = await client.get(f"{COMPANY_ENDPOINT}/{normalized}")

            if response.status_code == 200:
                data = response.json()
                return _parse_company(data)

            if response.status_code == 404:
                logger.info("Company not found: %s", formatted)
                return None

            raise HttpClientError(
                f"{API_BASE}{COMPANY_ENDPOINT}/{normalized}",
                response.status_code,
            )

    except HttpClientError:
        raise
    except Exception as exc:
        logger.error("Failed to get company %s: %s", formatted, exc)
        return None


async def get_company_officers(org_number: str) -> list[CompanyOfficer]:
    """Get board members and officers for a company.

    Args:
        org_number: Swedish org number (10 digits, with or without dash).
    """
    normalized = _normalize_org_number(org_number)

    headers = {"Accept": "application/json"}

    try:
        async with create_client(base_url=API_BASE, headers=headers) as client:
            response = await client.get(f"{COMPANY_ENDPOINT}/{normalized}/officers")

            if response.status_code == 200:
                data = response.json()
                officers_data = data if isinstance(data, list) else data.get("officers", [])
                return [_parse_officer(o) for o in officers_data]

            if response.status_code == 404:
                return []

            logger.warning(
                "Officers endpoint returned %d for %s",
                response.status_code,
                normalized,
            )
            return []

    except Exception as exc:
        logger.error("Failed to get officers for %s: %s", normalized, exc)
        return []


async def get_company_events(org_number: str) -> list[CompanyEvent]:
    """Get registration events/changes for a company.

    Args:
        org_number: Swedish org number (10 digits, with or without dash).
    """
    normalized = _normalize_org_number(org_number)

    headers = {"Accept": "application/json"}

    try:
        async with create_client(base_url=API_BASE, headers=headers) as client:
            response = await client.get(f"{COMPANY_ENDPOINT}/{normalized}/events")

            if response.status_code == 200:
                data = response.json()
                events_data = data if isinstance(data, list) else data.get("events", [])
                return [_parse_event(e) for e in events_data]

            if response.status_code == 404:
                return []

            logger.warning(
                "Events endpoint returned %d for %s",
                response.status_code,
                normalized,
            )
            return []

    except Exception as exc:
        logger.error("Failed to get events for %s: %s", normalized, exc)
        return []
