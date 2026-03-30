"""Feature: Riksdag & Regering — Swedish Parliament & Government data."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="riksdag",
    description="Riksdag & Regering: parliament members, votes, documents, debates",
    version="0.1.0",
    api_base="https://data.riksdagen.se",
    requires_auth=False,
    tags=["parliament", "government", "politics", "legislation", "votes"],
)
