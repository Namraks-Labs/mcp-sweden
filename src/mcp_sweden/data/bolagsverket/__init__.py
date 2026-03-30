"""Feature: Bolagsverket — Nordic Company Registry."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="bolagsverket",
    description="Bolagsverket: company search, registration data, annual reports",
    version="0.1.0",
    api_base="https://bolagsverket.se",
    requires_auth=False,
    tags=["companies", "business", "registration", "corporate"],
)
