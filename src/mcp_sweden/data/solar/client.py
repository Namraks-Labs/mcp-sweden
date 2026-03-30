"""HTTP clients for solar energy data APIs.

Three data sources:
  1. Energimyndigheten — embedded sample data for solar installations per municipality
  2. SMHI Open Data — point weather forecast for clearness index estimation
  3. mgrey.se/espot — Nord Pool day-ahead electricity prices for SE1–SE4
"""

from __future__ import annotations

import logging
import unicodedata
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from typing import Any

from mcp_sweden._shared.cache import ttl_cache
from mcp_sweden._shared.http_client import http_get
from mcp_sweden.data.solar.schemas import (
    MUNICIPALITY_DATA,
    PERFORMANCE_RATIO,
    PSH_TABLE,
    SAMPLE_INSTALLATIONS,
    WSYMB2_CLEARNESS,
    WSYMB2_DESCRIPTIONS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Energimyndigheten — solar installation data (embedded)
# ---------------------------------------------------------------------------


def _normalize(name: str) -> str:
    """Lowercase + strip diacritics for fuzzy matching."""
    nfd = unicodedata.normalize("NFD", name.lower())
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")


_NORMALIZED_MUNICIPALITIES: dict[str, str] = {_normalize(k): k for k in MUNICIPALITY_DATA}


def resolve_municipality(name: str) -> str | None:
    """Resolve a municipality name to its canonical form, or None."""
    if name in MUNICIPALITY_DATA:
        return name
    normalized = _normalize(name)
    return _NORMALIZED_MUNICIPALITIES.get(normalized)


def get_municipality_coords(name: str) -> tuple[float, float] | None:
    """Return (lat, lon) for a municipality, or None."""
    canonical = resolve_municipality(name)
    if canonical is None:
        return None
    lat, lon, _ = MUNICIPALITY_DATA[canonical]
    return (lat, lon)


def get_municipality_region(name: str) -> str | None:
    """Return SE region (SE1-SE4) for a municipality, or None."""
    canonical = resolve_municipality(name)
    if canonical is None:
        return None
    _, _, region = MUNICIPALITY_DATA[canonical]
    return region


def list_municipalities() -> list[str]:
    """Return sorted list of known municipality names."""
    return sorted(MUNICIPALITY_DATA.keys())


def get_installation_data(municipality_name: str) -> list[dict[str, Any]]:
    """Return installation records for a municipality, sorted by year."""
    canonical = resolve_municipality(municipality_name)
    if canonical is None:
        return []
    rows = [r for r in SAMPLE_INSTALLATIONS if r["municipality"] == canonical]
    return sorted(rows, key=lambda r: int(str(r["year"])))


def get_all_installation_data() -> list[dict[str, Any]]:
    """Return all installation records."""
    return list(SAMPLE_INSTALLATIONS)


# ---------------------------------------------------------------------------
# Solar formula
# ---------------------------------------------------------------------------


def peak_sun_hours(latitude: float, reference_date: date | None = None) -> float:
    """Return average daily peak sun hours for a given latitude and date."""
    if reference_date is None:
        reference_date = date.today()
    month_idx = reference_date.month - 1

    lat_bands = sorted(PSH_TABLE.keys())
    lat = max(lat_bands[0], min(lat_bands[-1], latitude))

    lower = max(b for b in lat_bands if b <= lat)
    upper = min(b for b in lat_bands if b >= lat)

    if lower == upper:
        return PSH_TABLE[lower][month_idx]

    frac = (lat - lower) / (upper - lower)
    psh_low = PSH_TABLE[lower][month_idx]
    psh_high = PSH_TABLE[upper][month_idx]
    return psh_low + frac * (psh_high - psh_low)


def expected_energy_kwh(
    capacity_kw: float,
    clearness_index: float,
    latitude: float,
    days: int = 1,
    reference_date: date | None = None,
) -> float:
    """Return expected electricity generation in kWh."""
    psh = peak_sun_hours(latitude, reference_date)
    return capacity_kw * clearness_index * psh * days * PERFORMANCE_RATIO


def clear_sky_energy_kwh(
    capacity_kw: float,
    latitude: float,
    days: int = 1,
    reference_date: date | None = None,
) -> float:
    """Return theoretical max generation assuming clear sky."""
    return expected_energy_kwh(capacity_kw, 1.0, latitude, days, reference_date)


# ---------------------------------------------------------------------------
# SMHI — weather forecast
# ---------------------------------------------------------------------------

_SMHI_BASE = (
    "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2"
    "/geotype/point/lon/{lon}/lat/{lat}/data.json"
)


@ttl_cache(ttl=1800)
async def fetch_smhi_forecast(lat: float, lon: float) -> list[dict[str, Any]]:
    """Fetch SMHI point forecast and return parsed hourly records."""
    url = _SMHI_BASE.format(lat=f"{lat:.4f}", lon=f"{lon:.4f}")
    payload = await http_get(url)

    def _extract(params: list[dict[str, Any]], name: str) -> float | None:
        for p in params:
            if p.get("name") == name:
                vals = p.get("values", [])
                return float(vals[0]) if vals else None
        return None

    records: list[dict[str, Any]] = []
    for entry in payload.get("timeSeries", []):
        params = entry.get("parameters", [])

        wsymb2 = int(_extract(params, "Wsymb2") or 3)
        temp = _extract(params, "t")

        # Cloud cover in oktas (0-8)
        tcc = _extract(params, "tcc_mean") or 0.0
        lcc = _extract(params, "lcc_mean") or 0.0
        mcc = _extract(params, "mcc_mean") or 0.0
        hcc = _extract(params, "hcc_mean") or 0.0

        # Weighted cloud-layer clearness (low clouds block more radiation)
        if tcc > 0 or lcc > 0 or mcc > 0 or hcc > 0:
            effective = (0.9 * lcc + 0.7 * mcc + 0.3 * hcc) / 8.0
            effective = max(0.0, min(1.0, effective))
            clearness = max(0.05, 1.0 - 0.95 * effective)
        else:
            clearness = WSYMB2_CLEARNESS.get(wsymb2, 0.10)

        valid_time_str = entry.get("validTime", "")
        try:
            valid_time = datetime.fromisoformat(valid_time_str.replace("Z", "+00:00"))
        except ValueError:
            continue

        records.append(
            {
                "valid_time": valid_time.isoformat(),
                "valid_hour": valid_time.hour,
                "wsymb2": wsymb2,
                "weather": WSYMB2_DESCRIPTIONS.get(wsymb2, f"Unknown ({wsymb2})"),
                "temperature": temp,
                "clearness": round(clearness, 3),
            }
        )

    return records


async def get_average_clearness(lat: float, lon: float, days_ahead: int = 7) -> tuple[float, str]:
    """Return (average_clearness, dominant_weather_description) over next N days.

    Only daytime hours (06-20 UTC) are considered.
    """
    records = await fetch_smhi_forecast(lat, lon)
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() + days_ahead * 86400

    daytime = []
    for r in records:
        try:
            vt = datetime.fromisoformat(r["valid_time"])
        except ValueError:
            continue
        if now.timestamp() < vt.timestamp() <= cutoff and 6 <= vt.hour <= 20:
            daytime.append(r)

    if not daytime:
        return 0.5, "Unknown"

    avg_clearness = sum(r["clearness"] for r in daytime) / len(daytime)

    symbol_counts = Counter(r["wsymb2"] for r in daytime)
    dominant = symbol_counts.most_common(1)[0][0]
    weather = WSYMB2_DESCRIPTIONS.get(dominant, f"Unknown ({dominant})")

    return round(avg_clearness, 3), weather


# ---------------------------------------------------------------------------
# Nord Pool — electricity prices via mgrey.se
# ---------------------------------------------------------------------------

_NORDPOOL_BASE = "https://mgrey.se/espot"
_VALID_AREAS = {"SE1", "SE2", "SE3", "SE4"}


@ttl_cache(ttl=1800)
async def fetch_electricity_prices(delivery_date: str = "today") -> dict[str, Any]:
    """Fetch day-ahead prices for all SE zones on a given date.

    Returns raw API response or error dict.
    """
    today = date.today()
    if delivery_date.lower() == "today":
        resolved = today.isoformat()
    elif delivery_date.lower() == "tomorrow":
        resolved = (today + timedelta(days=1)).isoformat()
    else:
        resolved = delivery_date

    try:
        raw = await http_get(_NORDPOOL_BASE, params={"format": "json", "date": resolved})
    except Exception as exc:
        logger.warning("Nord Pool price fetch failed: %s", exc)
        return {"error": str(exc), "date": resolved}

    return {"raw": raw, "date": resolved}


async def get_prices_for_areas(
    delivery_date: str = "today",
    currency: str = "SEK",
    areas: list[str] | None = None,
) -> dict[str, Any]:
    """Return structured price data for specified SE zones."""
    if areas is None:
        areas = ["SE1", "SE2", "SE3", "SE4"]

    currency = currency.upper()
    if currency not in {"SEK", "EUR"}:
        currency = "SEK"

    price_field = "price_sek" if currency == "SEK" else "price_eur"

    data = await fetch_electricity_prices(delivery_date)
    if "error" in data:
        return {"error": data["error"], "date": data.get("date", delivery_date)}

    raw = data["raw"]
    resolved_date = data["date"]

    result_areas: dict[str, list[dict[str, Any]]] = {}
    for area in areas:
        if area not in _VALID_AREAS:
            continue
        hourly_raw = raw.get(area, [])
        # Convert from öre/kWh to SEK/MWh (multiply by 10)
        result_areas[area] = [
            {"hour": entry["hour"], "price": round(entry[price_field] * 10, 2)}
            for entry in hourly_raw
        ]

    return {
        "date": resolved_date,
        "currency": currency,
        "unit": f"{currency}/MWh",
        "areas": result_areas,
    }


async def get_average_price(
    area: str, delivery_date: str = "today", currency: str = "SEK"
) -> float | None:
    """Return average day-ahead price for one area, or None if unavailable."""
    data = await get_prices_for_areas(delivery_date=delivery_date, currency=currency, areas=[area])
    if "error" in data:
        return None
    hourly = data.get("areas", {}).get(area, [])
    if not hourly:
        return None
    avg: float = round(sum(e["price"] for e in hourly) / len(hourly), 2)
    return avg
