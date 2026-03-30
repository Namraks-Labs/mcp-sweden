"""Feature: Solar — Swedish Solar Energy Data.

Data sources:
  - Energimyndigheten: solar panel installation statistics (embedded sample data)
  - SMHI Open Data: weather forecasts for clearness index estimation
  - mgrey.se/espot: Nord Pool day-ahead electricity prices (SE1–SE4)

Reference: j-jayes/solar-sweden-mcp
"""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="solar",
    description="Solar: solar energy production, irradiance, installations in Sweden",
    version="0.1.0",
    api_base="https://opendata-download-metfcst.smhi.se",
    requires_auth=False,
    tags=["energy", "solar", "renewable", "electricity", "climate"],
)
