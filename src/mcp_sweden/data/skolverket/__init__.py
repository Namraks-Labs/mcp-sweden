"""Feature: Skolverket — National Agency for Education."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="skolverket",
    description="Skolverket: school registry, statistics, grades, teacher data",
    version="0.1.0",
    api_base="https://api.skolverket.se",
    requires_auth=False,
    tags=["education", "schools", "grades", "statistics", "teachers"],
)
