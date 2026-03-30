"""Feature: Sveriges Radio — Swedish Public Radio."""

from mcp_sweden._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="sverigesradio",
    description="Sveriges Radio: channels, programs, episodes, playlists, news, traffic",
    version="0.1.0",
    api_base="https://api.sr.se/api/v2",
    requires_auth=False,
    tags=["radio", "media", "news", "programs", "audio", "traffic"],
)
