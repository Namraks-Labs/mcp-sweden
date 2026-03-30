"""Tests for the Bolagsverket feature — schemas, client helpers, and tools."""

from __future__ import annotations

import pytest

from mcp_sweden.data.bolagsverket.client import (
    _format_org_number,
    _normalize_org_number,
    _parse_company,
    _parse_event,
    _parse_officer,
)
from mcp_sweden.data.bolagsverket.schemas import (
    Company,
    CompanyAddress,
    CompanyEvent,
    CompanyOfficer,
    CompanySearchResult,
)

# ---------------------------------------------------------------------------
# Org number helpers
# ---------------------------------------------------------------------------


class TestNormalizeOrgNumber:
    def test_ten_digits(self) -> None:
        assert _normalize_org_number("5560123456") == "5560123456"

    def test_with_dash(self) -> None:
        assert _normalize_org_number("556012-3456") == "5560123456"

    def test_twelve_digits_strips_century(self) -> None:
        assert _normalize_org_number("165560123456") == "5560123456"

    def test_with_spaces(self) -> None:
        assert _normalize_org_number("556012 3456") == "5560123456"

    def test_invalid_length_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid org number"):
            _normalize_org_number("12345")

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid org number"):
            _normalize_org_number("")


class TestFormatOrgNumber:
    def test_format(self) -> None:
        assert _format_org_number("5560123456") == "556012-3456"

    def test_format_with_dash(self) -> None:
        assert _format_org_number("556012-3456") == "556012-3456"


# ---------------------------------------------------------------------------
# Schema models
# ---------------------------------------------------------------------------


class TestCompanySchema:
    def test_format_full(self) -> None:
        company = Company(
            org_number="556012-3456",
            name="Test AB",
            company_type="AB",
            status="Active",
            registration_date="2020-01-15",
            address=CompanyAddress(street="Kungsgatan 1", postal_code="111 22", city="Stockholm"),
            business_description="Software development",
            share_capital="50000 SEK",
            num_employees="10-19",
        )
        text = company.format()
        assert "Test AB" in text
        assert "556012-3456" in text
        assert "AB" in text
        assert "Active" in text
        assert "Software development" in text
        assert "Kungsgatan 1" in text

    def test_format_minimal(self) -> None:
        company = Company(org_number="5560123456", name="Minimal AB")
        text = company.format()
        assert "Minimal AB" in text
        assert "5560123456" in text


class TestCompanyOfficerSchema:
    def test_format_with_date(self) -> None:
        officer = CompanyOfficer(
            name="Anna Svensson",
            role="Styrelseledamot",
            appointed_date="2021-03-01",
        )
        text = officer.format()
        assert "Anna Svensson" in text
        assert "Styrelseledamot" in text
        assert "2021-03-01" in text

    def test_format_without_date(self) -> None:
        officer = CompanyOfficer(name="Erik Johansson", role="VD")
        text = officer.format()
        assert "Erik Johansson" in text
        assert "VD" in text


class TestCompanyEventSchema:
    def test_format_with_description(self) -> None:
        event = CompanyEvent(
            date="2023-06-15",
            event_type="Board change",
            description="New board member appointed",
        )
        text = event.format()
        assert "2023-06-15" in text
        assert "Board change" in text
        assert "New board member appointed" in text

    def test_format_without_description(self) -> None:
        event = CompanyEvent(date="2023-01-01", event_type="Annual report filed")
        text = event.format()
        assert "Annual report filed" in text


class TestSearchResultSchema:
    def test_format_empty(self) -> None:
        result = CompanySearchResult(query="nonexistent")
        assert "No companies found" in result.format()

    def test_format_with_results(self) -> None:
        result = CompanySearchResult(
            companies=[
                Company(org_number="5560123456", name="Foo AB", company_type="AB"),
                Company(org_number="5560654321", name="Bar HB", company_type="HB"),
            ],
            total_count=2,
            page=1,
            query="test",
        )
        text = result.format()
        assert "Found 2 companies" in text
        assert "Foo AB" in text
        assert "Bar HB" in text


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


class TestParseCompany:
    def test_parse_full_record(self) -> None:
        data = {
            "organisationNumber": "5560123456",
            "name": "Parsed AB",
            "companyForm": "AB",
            "status": "Active",
            "registrationDate": "2020-01-01",
            "address": {
                "street": "Storgatan 1",
                "postalCode": "111 22",
                "city": "Stockholm",
            },
            "businessDescription": "Consulting",
            "shareCapital": "100000 SEK",
            "numberOfEmployees": "5-9",
        }
        company = _parse_company(data)
        assert company.org_number == "5560123456"
        assert company.name == "Parsed AB"
        assert company.company_type == "AB"
        assert company.address.city == "Stockholm"

    def test_parse_empty_record(self) -> None:
        company = _parse_company({})
        assert company.org_number == ""
        assert company.name == ""

    def test_parse_alternative_keys(self) -> None:
        data = {
            "orgNumber": "5560001111",
            "companyName": "Alt AB",
            "type": "AB",
            "registrationStatus": "Dissolved",
            "address": {"zipCode": "222 33", "town": "Göteborg"},
        }
        company = _parse_company(data)
        assert company.org_number == "5560001111"
        assert company.name == "Alt AB"
        assert company.status == "Dissolved"
        assert company.address.city == "Göteborg"


class TestParseOfficer:
    def test_parse(self) -> None:
        data = {
            "name": "Test Person",
            "role": "VD",
            "appointedDate": "2022-01-01",
        }
        officer = _parse_officer(data)
        assert officer.name == "Test Person"
        assert officer.role == "VD"
        assert officer.appointed_date == "2022-01-01"

    def test_parse_alternative_keys(self) -> None:
        data = {"fullName": "Alt Person", "title": "Ordförande", "since": "2021-06-15"}
        officer = _parse_officer(data)
        assert officer.name == "Alt Person"
        assert officer.role == "Ordförande"


class TestParseEvent:
    def test_parse(self) -> None:
        data = {
            "date": "2023-05-01",
            "type": "Name change",
            "description": "Company renamed",
        }
        event = _parse_event(data)
        assert event.date == "2023-05-01"
        assert event.event_type == "Name change"

    def test_parse_alternative_keys(self) -> None:
        data = {"eventDate": "2023-01-01", "eventType": "Filing", "text": "Filed annual report"}
        event = _parse_event(data)
        assert event.date == "2023-01-01"
        assert event.event_type == "Filing"
        assert event.description == "Filed annual report"


# ---------------------------------------------------------------------------
# Feature metadata
# ---------------------------------------------------------------------------


class TestFeatureMeta:
    def test_meta_exists(self) -> None:
        from mcp_sweden.data.bolagsverket import FEATURE_META

        assert FEATURE_META.name == "bolagsverket"
        assert FEATURE_META.requires_auth is False
        assert "companies" in FEATURE_META.tags

    def test_server_has_tools(self) -> None:
        from mcp_sweden.data.bolagsverket.server import mcp

        assert mcp is not None
        assert mcp.name == "mcp-sweden-bolagsverket"
