"""Feature: SCB — Statistics Sweden (Statistiska Centralbyran)."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="scb",
    description="SCB: population, economy, labor, trade, environment statistics",
    version="0.1.0",
    api_base="https://api.scb.se/OV0104/v1/doris",
    requires_auth=False,
    tags=["statistics", "population", "economy", "demographics", "labor"],
)
