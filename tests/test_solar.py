"""Tests for the Solar feature — client helpers, formulas, and tools."""

from __future__ import annotations

from datetime import date

import pytest

from mcp_sweden.data.solar.client import (
    clear_sky_energy_kwh,
    expected_energy_kwh,
    get_installation_data,
    get_municipality_coords,
    get_municipality_region,
    list_municipalities,
    peak_sun_hours,
    resolve_municipality,
)
from mcp_sweden.data.solar.schemas import (
    MUNICIPALITY_DATA,
    PSH_TABLE,
    SAMPLE_INSTALLATIONS,
    WSYMB2_CLEARNESS,
    WSYMB2_DESCRIPTIONS,
)

# ---------------------------------------------------------------------------
# Municipality resolution
# ---------------------------------------------------------------------------


class TestResolveMunicipality:
    def test_exact_match(self) -> None:
        assert resolve_municipality("Stockholm") == "Stockholm"

    def test_case_insensitive(self) -> None:
        assert resolve_municipality("stockholm") == "Stockholm"

    def test_diacritic_stripped(self) -> None:
        assert resolve_municipality("Goteborg") == "Göteborg"
        assert resolve_municipality("Malmo") == "Malmö"
        assert resolve_municipality("Orebro") == "Örebro"

    def test_not_found(self) -> None:
        assert resolve_municipality("Nonexistent") is None


class TestMunicipalityCoords:
    def test_known_municipality(self) -> None:
        coords = get_municipality_coords("Stockholm")
        assert coords is not None
        lat, lon = coords
        assert 59.0 < lat < 60.0
        assert 17.0 < lon < 19.0

    def test_unknown_returns_none(self) -> None:
        assert get_municipality_coords("FakeCity") is None


class TestMunicipalityRegion:
    def test_se4_malmö(self) -> None:
        assert get_municipality_region("Malmö") == "SE4"

    def test_se3_stockholm(self) -> None:
        assert get_municipality_region("Stockholm") == "SE3"

    def test_se1_luleå(self) -> None:
        assert get_municipality_region("Luleå") == "SE1"

    def test_se2_umeå(self) -> None:
        assert get_municipality_region("Umeå") == "SE2"


class TestListMunicipalities:
    def test_returns_sorted(self) -> None:
        munis = list_municipalities()
        assert munis == sorted(munis)
        assert len(munis) > 10


# ---------------------------------------------------------------------------
# Installation data
# ---------------------------------------------------------------------------


class TestInstallationData:
    def test_known_municipality(self) -> None:
        rows = get_installation_data("Stockholm")
        assert len(rows) > 0
        assert rows[0]["municipality"] == "Stockholm"
        # Should be sorted by year
        years = [int(str(r["year"])) for r in rows]
        assert years == sorted(years)

    def test_case_insensitive(self) -> None:
        rows = get_installation_data("malmö")
        assert len(rows) > 0
        assert rows[0]["municipality"] == "Malmö"

    def test_unknown_returns_empty(self) -> None:
        assert get_installation_data("FakeCity") == []


# ---------------------------------------------------------------------------
# Solar formula
# ---------------------------------------------------------------------------


class TestPeakSunHours:
    def test_summer_higher_than_winter(self) -> None:
        summer = peak_sun_hours(59.0, date(2024, 6, 15))
        winter = peak_sun_hours(59.0, date(2024, 12, 15))
        assert summer > winter

    def test_south_higher_than_north(self) -> None:
        south = peak_sun_hours(55.0, date(2024, 6, 15))
        north = peak_sun_hours(66.0, date(2024, 6, 15))
        assert south > north

    def test_interpolation(self) -> None:
        # Latitude 58 is between 57 and 59
        psh = peak_sun_hours(58.0, date(2024, 6, 15))
        psh_57 = peak_sun_hours(57.0, date(2024, 6, 15))
        psh_59 = peak_sun_hours(59.0, date(2024, 6, 15))
        assert psh_57 >= psh >= psh_59  # south gets more sun


class TestExpectedEnergy:
    def test_clear_sky_higher_than_cloudy(self) -> None:
        clear = expected_energy_kwh(100, 1.0, 59.0, 1, date(2024, 6, 15))
        cloudy = expected_energy_kwh(100, 0.3, 59.0, 1, date(2024, 6, 15))
        assert clear > cloudy

    def test_more_days_more_energy(self) -> None:
        one_day = expected_energy_kwh(100, 0.5, 59.0, 1, date(2024, 6, 15))
        seven_days = expected_energy_kwh(100, 0.5, 59.0, 7, date(2024, 6, 15))
        assert seven_days == pytest.approx(one_day * 7, rel=1e-6)

    def test_clear_sky_is_clearness_one(self) -> None:
        clear = clear_sky_energy_kwh(100, 59.0, 1, date(2024, 6, 15))
        manual = expected_energy_kwh(100, 1.0, 59.0, 1, date(2024, 6, 15))
        assert clear == pytest.approx(manual, rel=1e-6)


# ---------------------------------------------------------------------------
# Schemas data integrity
# ---------------------------------------------------------------------------


class TestSchemaData:
    def test_all_wsymb2_codes_have_clearness(self) -> None:
        for code in range(1, 28):
            assert code in WSYMB2_CLEARNESS

    def test_all_wsymb2_codes_have_description(self) -> None:
        for code in range(1, 28):
            assert code in WSYMB2_DESCRIPTIONS

    def test_clearness_values_in_range(self) -> None:
        for val in WSYMB2_CLEARNESS.values():
            assert 0.0 <= val <= 1.0

    def test_psh_table_has_12_months(self) -> None:
        for lat, months in PSH_TABLE.items():
            assert len(months) == 12, f"Latitude {lat} has {len(months)} months"

    def test_municipality_data_has_valid_regions(self) -> None:
        valid = {"SE1", "SE2", "SE3", "SE4"}
        for name, (lat, lon, region) in MUNICIPALITY_DATA.items():
            assert region in valid, f"{name} has invalid region {region}"
            assert 55.0 <= lat <= 70.0, f"{name} has invalid latitude {lat}"
            assert 10.0 <= lon <= 25.0, f"{name} has invalid longitude {lon}"

    def test_sample_installations_consistent(self) -> None:
        for row in SAMPLE_INSTALLATIONS:
            assert isinstance(row["municipality"], str)
            assert isinstance(row["year"], int)
            assert isinstance(row["num_installations"], int)
            assert isinstance(row["capacity_kw"], float)
            assert float(str(row["capacity_kw"])) > 0


# ---------------------------------------------------------------------------
# Feature metadata
# ---------------------------------------------------------------------------


class TestFeatureMeta:
    def test_meta_exists(self) -> None:
        from mcp_sweden.data.solar import FEATURE_META

        assert FEATURE_META.name == "solar"
        assert FEATURE_META.requires_auth is False
        assert "energy" in FEATURE_META.tags

    def test_server_has_mcp(self) -> None:
        from mcp_sweden.data.solar.server import mcp

        assert mcp is not None
        assert mcp.name == "mcp-sweden-solar"


# ---------------------------------------------------------------------------
# Tool functions (unit tests — no network calls)
# ---------------------------------------------------------------------------


class TestToolSolarInstallations:
    @pytest.mark.asyncio
    async def test_single_municipality(self) -> None:
        from mcp_sweden.data.solar.tools import solar_installations

        result = await solar_installations("Stockholm")
        assert "error" not in result
        assert result["municipality"] == "Stockholm"
        assert result["latest_capacity_kw"] > 0
        assert len(result["data"]) > 0

    @pytest.mark.asyncio
    async def test_summary_mode(self) -> None:
        from mcp_sweden.data.solar.tools import solar_installations

        result = await solar_installations()
        assert "error" not in result
        assert result["total_municipalities"] > 0
        assert result["total_capacity_kw"] > 0

    @pytest.mark.asyncio
    async def test_unknown_municipality(self) -> None:
        from mcp_sweden.data.solar.tools import solar_installations

        result = await solar_installations("FakeCity")
        assert "error" in result
        assert "available" in result


class TestToolSolarGrowth:
    @pytest.mark.asyncio
    async def test_growth_calculation(self) -> None:
        from mcp_sweden.data.solar.tools import solar_growth

        result = await solar_growth("Stockholm")
        assert "error" not in result
        assert result["municipality"] == "Stockholm"
        assert result["cagr"] is not None
        assert result["cagr"] > 0
        assert len(result["yoy_growth"]) > 0
        # All growth should be positive for Swedish solar
        for entry in result["yoy_growth"]:
            assert entry["growth_pct"] is None or entry["growth_pct"] > 0

    @pytest.mark.asyncio
    async def test_unknown_municipality(self) -> None:
        from mcp_sweden.data.solar.tools import solar_growth

        result = await solar_growth("FakeCity")
        assert "error" in result
