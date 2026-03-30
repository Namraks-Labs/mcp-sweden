"""Feature: Kolada — Municipality & Region Statistics."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="kolada",
    description="Kolada: municipality & region KPIs, comparisons, rankings",
    version="0.1.0",
    api_base="https://api.kolada.se/v2",
    requires_auth=False,
    tags=["municipalities", "regions", "kpi", "local-government", "comparisons"],
)
