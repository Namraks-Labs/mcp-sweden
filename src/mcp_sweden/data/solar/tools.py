"""Tool implementations for the Solar feature.

Five tools:
  1. solar_installations — current solar panel stats for a municipality
  2. solar_growth — historical growth with YoY and CAGR
  3. solar_forecast — weather-based generation forecast
  4. electricity_prices — Nord Pool day-ahead prices for SE zones
  5. solar_revenue — estimated revenue combining all three data sources
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from mcp_sweden.data.solar.client import (
    clear_sky_energy_kwh,
    expected_energy_kwh,
    get_all_installation_data,
    get_average_clearness,
    get_average_price,
    get_installation_data,
    get_municipality_coords,
    get_municipality_region,
    get_prices_for_areas,
    list_municipalities,
    resolve_municipality,
)


async def solar_installations(municipality: str | None = None) -> dict[str, Any]:
    """Get solar panel installation statistics for Swedish municipalities.

    Shows number of installations and installed capacity (kW) per year.
    If no municipality is given, returns a summary of all municipalities
    with their latest data.

    Args:
        municipality: Swedish municipality name (e.g. "Stockholm", "Malmö").
                     Case-insensitive, handles both "Göteborg" and "Goteborg".
                     Omit to get a summary of all municipalities.
    """
    if municipality:
        canonical = resolve_municipality(municipality)
        if canonical is None:
            return {
                "error": f"Municipality '{municipality}' not found.",
                "available": list_municipalities(),
            }

        rows = get_installation_data(canonical)
        if not rows:
            return {"error": f"No installation data for '{canonical}'."}

        latest = rows[-1]
        return {
            "municipality": canonical,
            "data": rows,
            "latest_year": latest["year"],
            "latest_installations": latest["num_installations"],
            "latest_capacity_kw": latest["capacity_kw"],
            "summary": (
                f"{canonical} had {latest['num_installations']:,} solar installations "
                f"with {float(str(latest['capacity_kw'])):,.0f} kW capacity in {latest['year']}."
            ),
        }

    # Summary mode: latest data per municipality
    all_data = get_all_installation_data()
    latest_by_muni: dict[str, dict[str, Any]] = {}
    for row in all_data:
        muni = str(row["municipality"])
        yr = int(str(row["year"]))
        if muni not in latest_by_muni or yr > int(str(latest_by_muni[muni]["year"])):
            latest_by_muni[muni] = dict(row)

    municipalities = sorted(
        latest_by_muni.values(),
        key=lambda r: float(str(r["capacity_kw"])),
        reverse=True,
    )

    total_capacity = sum(float(str(r["capacity_kw"])) for r in municipalities)
    total_installations = sum(int(str(r["num_installations"])) for r in municipalities)

    return {
        "municipalities": municipalities,
        "total_municipalities": len(municipalities),
        "total_capacity_kw": total_capacity,
        "total_installations": total_installations,
        "summary": (
            f"{len(municipalities)} municipalities tracked with "
            f"{total_installations:,} installations totaling "
            f"{total_capacity:,.0f} kW capacity."
        ),
    }


async def solar_growth(municipality: str) -> dict[str, Any]:
    """Get historical solar installation growth for a Swedish municipality.

    Returns year-over-year percentage growth and compound annual growth rate (CAGR)
    for installed solar capacity.

    Args:
        municipality: Swedish municipality name (e.g. "Stockholm", "Lund").
    """
    canonical = resolve_municipality(municipality)
    if canonical is None:
        return {
            "error": f"Municipality '{municipality}' not found.",
            "available": list_municipalities(),
        }

    rows = get_installation_data(canonical)
    if not rows:
        return {"error": f"No installation data for '{canonical}'."}

    # Year-over-year growth
    yoy: list[dict[str, Any]] = []
    for i in range(1, len(rows)):
        prev_cap = float(str(rows[i - 1]["capacity_kw"]))
        curr_cap = float(str(rows[i]["capacity_kw"]))
        pct = round((curr_cap - prev_cap) / prev_cap * 100, 1) if prev_cap > 0 else None
        yoy.append({
            "year": rows[i]["year"],
            "capacity_kw": curr_cap,
            "growth_pct": pct,
        })

    # CAGR
    cagr: float | None = None
    if len(rows) >= 2:
        first_cap = float(str(rows[0]["capacity_kw"]))
        last_cap = float(str(rows[-1]["capacity_kw"]))
        n_years = int(str(rows[-1]["year"])) - int(str(rows[0]["year"]))
        if n_years > 0 and first_cap > 0:
            cagr = round(((last_cap / first_cap) ** (1 / n_years) - 1) * 100, 1)

    latest = rows[-1]
    latest_yoy = yoy[-1]["growth_pct"] if yoy else None

    parts = [
        f"{canonical} had {latest['num_installations']:,} solar installations "
        f"with {float(str(latest['capacity_kw'])):,.0f} kW capacity in {latest['year']}."
    ]
    if latest_yoy is not None:
        parts.append(f"Capacity grew {latest_yoy:.1f}% in {latest['year']}.")
    if cagr is not None:
        n = int(str(rows[-1]["year"])) - int(str(rows[0]["year"]))
        parts.append(f"{n}-year CAGR: {cagr:.1f}%.")

    return {
        "municipality": canonical,
        "data": rows,
        "yoy_growth": yoy,
        "cagr": cagr,
        "latest_year": latest["year"],
        "latest_capacity_kw": latest["capacity_kw"],
        "latest_installations": latest["num_installations"],
        "summary": " ".join(parts),
    }


async def solar_forecast(
    municipality: str,
    days_ahead: int = 7,
) -> dict[str, Any]:
    """Forecast solar energy generation for a Swedish municipality.

    Combines installed capacity with SMHI weather forecast to estimate
    expected electricity generation vs clear-sky maximum.

    Args:
        municipality: Swedish municipality name.
        days_ahead: Number of days to forecast (1-9, default 7).
    """
    days_ahead = max(1, min(9, days_ahead))

    canonical = resolve_municipality(municipality)
    if canonical is None:
        return {
            "error": f"Municipality '{municipality}' not found.",
            "available": list_municipalities(),
        }

    rows = get_installation_data(canonical)
    if not rows:
        return {"error": f"No installation data for '{canonical}'."}

    latest = rows[-1]
    capacity_kw = float(str(latest["capacity_kw"]))

    coords = get_municipality_coords(canonical)
    if coords is None:
        return {"error": f"Coordinates not found for '{canonical}'."}
    lat, lon = coords

    clearness, weather = await get_average_clearness(lat, lon, days_ahead)

    today = date.today()
    forecast_kwh = expected_energy_kwh(capacity_kw, clearness, lat, days_ahead, today)
    clear_kwh = clear_sky_energy_kwh(capacity_kw, lat, days_ahead, today)
    loss_kwh = clear_kwh - forecast_kwh
    loss_pct = (loss_kwh / clear_kwh * 100) if clear_kwh > 0 else 0.0

    return {
        "municipality": canonical,
        "days_ahead": days_ahead,
        "installed_capacity_kw": capacity_kw,
        "data_year": latest["year"],
        "forecast_kwh": round(forecast_kwh, 1),
        "clear_sky_kwh": round(clear_kwh, 1),
        "cloud_loss_kwh": round(loss_kwh, 1),
        "cloud_loss_pct": round(loss_pct, 1),
        "avg_clearness": clearness,
        "dominant_weather": weather,
        "summary": (
            f"Over the next {days_ahead} day(s), {canonical}'s {capacity_kw:,.0f} kW "
            f"is forecast to generate {forecast_kwh:,.0f} kWh. "
            f"Clear-sky max: {clear_kwh:,.0f} kWh. "
            f"Cloud cover ({weather}) reduces output by {loss_pct:.1f}%."
        ),
    }


async def electricity_prices(
    delivery_date: str = "today",
    currency: str = "SEK",
    areas: str = "SE1,SE2,SE3,SE4",
) -> dict[str, Any]:
    """Get day-ahead electricity spot prices for Swedish pricing zones.

    Data from Nord Pool via mgrey.se. Prices are per MWh.

    Args:
        delivery_date: "today", "tomorrow", or ISO date "YYYY-MM-DD".
        currency: "SEK" (default) or "EUR".
        areas: Comma-separated SE zones, e.g. "SE3,SE4". Default: all four.
    """
    area_list = [a.strip().upper() for a in areas.split(",")]

    data = await get_prices_for_areas(delivery_date, currency, area_list)
    if "error" in data:
        return {
            "error": data["error"],
            "date": data.get("date", delivery_date),
            "note": "Tomorrow's prices are published around 13:00 CET.",
        }

    resolved_date = data["date"]
    currency_used = data["currency"]
    raw_areas = data.get("areas", {})

    area_names = {
        "SE1": "Luleå (Northern Sweden)",
        "SE2": "Sundsvall (Central-North)",
        "SE3": "Stockholm (Central)",
        "SE4": "Malmö (Southern Sweden)",
    }

    prices: dict[str, Any] = {}
    averages: dict[str, float] = {}

    for area, hourly in raw_areas.items():
        if not hourly:
            continue
        values = [h["price"] for h in hourly]
        avg = round(sum(values) / len(values), 2)
        averages[area] = avg
        prices[area] = {
            "name": area_names.get(area, area),
            "avg": avg,
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "hourly": hourly,
        }

    if not averages:
        return {"error": f"No price data for {resolved_date}.", "date": resolved_date}

    cheapest = min(averages, key=averages.get)  # type: ignore[arg-type]
    most_expensive = max(averages, key=averages.get)  # type: ignore[arg-type]

    parts = [f"Day-ahead prices for {resolved_date} ({currency_used}/MWh):"]
    for area in ["SE1", "SE2", "SE3", "SE4"]:
        if area in averages:
            parts.append(f"  {area}: {averages[area]:.1f}")

    return {
        "date": resolved_date,
        "currency": currency_used,
        "unit": f"{currency_used}/MWh",
        "prices": prices,
        "cheapest_area": cheapest,
        "most_expensive_area": most_expensive,
        "summary": " ".join(parts),
    }


async def solar_revenue(
    municipality: str,
    days_ahead: int = 1,
    currency: str = "SEK",
) -> dict[str, Any]:
    """Estimate solar electricity revenue for a Swedish municipality.

    Combines three data sources:
    - Energimyndigheten: installed solar capacity
    - SMHI: weather forecast for clearness index
    - Nord Pool: day-ahead electricity prices

    Args:
        municipality: Swedish municipality name.
        days_ahead: 0=today, 1=tomorrow (default), up to 9.
        currency: "SEK" (default) or "EUR".
    """
    days_ahead = max(0, min(9, days_ahead))
    currency = currency.upper()
    if currency not in {"SEK", "EUR"}:
        currency = "SEK"

    canonical = resolve_municipality(municipality)
    if canonical is None:
        return {
            "error": f"Municipality '{municipality}' not found.",
            "available": list_municipalities(),
        }

    rows = get_installation_data(canonical)
    if not rows:
        return {"error": f"No installation data for '{canonical}'."}

    latest = rows[-1]
    capacity_kw = float(str(latest["capacity_kw"]))

    coords = get_municipality_coords(canonical)
    if coords is None:
        return {"error": f"Coordinates not found for '{canonical}'."}
    lat, lon = coords

    se_region = get_municipality_region(canonical) or "SE3"

    # Delivery date
    today = date.today()
    delivery_date = today + timedelta(days=days_ahead)
    delivery_str = delivery_date.isoformat()
    if days_ahead == 0:
        date_label = "today"
    elif days_ahead == 1:
        date_label = "tomorrow"
    else:
        date_label = f"in {days_ahead} days"

    # Weather forecast
    clearness, weather = await get_average_clearness(
        lat, lon, max(1, days_ahead),
    )

    # Generation estimates
    forecast_kwh = expected_energy_kwh(
        capacity_kw, clearness, lat, max(1, days_ahead), delivery_date,
    )
    clear_kwh = clear_sky_energy_kwh(capacity_kw, lat, max(1, days_ahead), delivery_date)

    # Electricity price
    avg_price = await get_average_price(se_region, delivery_str, currency)

    if avg_price is None:
        return {
            "municipality": canonical,
            "se_region": se_region,
            "delivery_date": delivery_str,
            "currency": currency,
            "capacity_kw": capacity_kw,
            "forecast_kwh": round(forecast_kwh, 1),
            "clear_sky_kwh": round(clear_kwh, 1),
            "avg_clearness": clearness,
            "dominant_weather": weather,
            "price_note": "Price data not yet available. Nord Pool publishes around 13:00 CET.",
            "summary": (
                f"{canonical} ({se_region}) forecast: {forecast_kwh:,.0f} kWh {date_label}. "
                f"Price data not yet available."
            ),
        }

    price_per_kwh = avg_price / 1000
    revenue = round(forecast_kwh * price_per_kwh, 2)
    clear_revenue = round(clear_kwh * price_per_kwh, 2)
    cloud_loss = round(clear_revenue - revenue, 2)

    return {
        "municipality": canonical,
        "se_region": se_region,
        "delivery_date": delivery_str,
        "currency": currency,
        "capacity_kw": capacity_kw,
        "data_year": latest["year"],
        "forecast_kwh": round(forecast_kwh, 1),
        "clear_sky_kwh": round(clear_kwh, 1),
        "avg_clearness": clearness,
        "dominant_weather": weather,
        "avg_price_per_mwh": avg_price,
        "estimated_revenue": revenue,
        "clear_sky_revenue": clear_revenue,
        "cloud_revenue_loss": cloud_loss,
        "summary": (
            f"{canonical} ({se_region}) forecast: {forecast_kwh:,.0f} kWh {date_label} "
            f"({delivery_str}), worth ~{revenue:,.0f} {currency} at "
            f"{avg_price:.1f} {currency}/MWh. "
            f"Clear-sky max: {clear_kwh:,.0f} kWh ({clear_revenue:,.0f} {currency}). "
            f"Cloud cover ({weather}) costs ~{cloud_loss:,.0f} {currency}."
        ),
    }
