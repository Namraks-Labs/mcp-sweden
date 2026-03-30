"""Feature: SL — Stockholm Public Transport (Storstockholms Lokaltrafik)."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="sl",
    description="SL: Stockholm public transport — stations, real-time departures, lines",
    version="0.1.0",
    api_base="https://transport.integration.sl.se/v1",
    requires_auth=False,
    tags=["transport", "stockholm", "metro", "bus", "tram", "train", "departures"],
)
