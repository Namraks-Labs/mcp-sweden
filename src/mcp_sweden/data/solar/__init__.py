"""Feature: Solar — Swedish Solar Energy Data."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="solar",
    description="Solar: solar energy production, irradiance, installations in Sweden",
    version="0.1.0",
    api_base="",
    requires_auth=False,
    tags=["energy", "solar", "renewable", "electricity", "climate"],
)
