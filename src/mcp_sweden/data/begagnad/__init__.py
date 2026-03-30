"""Feature: Begagnad — Second-hand Marketplaces."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="begagnad",
    description="Begagnad: second-hand marketplace listings, price tracking",
    version="0.1.0",
    api_base="",
    requires_auth=False,
    tags=["marketplace", "second-hand", "prices", "listings", "sustainability"],
)
