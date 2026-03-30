"""Feature metadata and auto-registry for mcp-sweden.

Any subpackage that exports a FEATURE_META and has a server.py with an `mcp`
object will be automatically discovered, validated, and mounted on the root server.

Adapted from mcp-brasil's convention-based auto-discovery pattern.

Usage:
    from fastmcp import FastMCP
    from mcp_sweden._shared.feature import FeatureRegistry

    mcp = FastMCP("mcp-sweden")
    registry = FeatureRegistry()
    registry.discover("mcp_sweden.data")
    registry.mount_all(mcp)
"""

from __future__ import annotations

import importlib
import logging
import os
import pkgutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import mcp_sweden.settings  # noqa: F401 — ensure .env is loaded

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FeatureMeta:
    """Declarative metadata for a feature.

    Every feature must export a FEATURE_META instance in its __init__.py.

    Example:
        from mcp_sweden._shared.feature import FeatureMeta

        FEATURE_META = FeatureMeta(
            name="riksdag",
            description="Riksdag & Regering: parliament data, votes, documents",
            api_base="https://data.riksdagen.se",
        )
    """

    name: str
    description: str
    version: str = "0.1.0"
    api_base: str = ""
    requires_auth: bool = False
    auth_env_var: str | None = None
    enabled: bool = True
    tags: list[str] = field(default_factory=list)

    def is_auth_available(self) -> bool:
        """Check if required auth credentials are available."""
        if not self.requires_auth:
            return True
        if self.auth_env_var is None:
            return False
        return bool(os.environ.get(self.auth_env_var))


@dataclass
class RegisteredFeature:
    """A feature that has been discovered, validated, and registered."""

    meta: FeatureMeta
    server: FastMCP
    module_path: str


class FeatureRegistry:
    """Auto-registry that discovers, validates, and mounts features.

    Convention (all required for auto-discovery):
        1. Subpackage under the scanned package
        2. Name does NOT start with '_'
        3. __init__.py exports FEATURE_META: FeatureMeta
        4. server.py exports mcp: FastMCP
        5. If requires_auth=True, auth_env_var must be set in env
    """

    def __init__(self) -> None:
        self._features: dict[str, RegisteredFeature] = {}
        self._skipped: dict[str, str] = {}

    @property
    def features(self) -> dict[str, RegisteredFeature]:
        return dict(self._features)

    @property
    def skipped(self) -> dict[str, str]:
        return dict(self._skipped)

    def discover(self, package_name: str = "mcp_sweden.data") -> FeatureRegistry:
        """Discover all features in the package."""
        package = importlib.import_module(package_name)

        for _finder, name, ispkg in pkgutil.iter_modules(
            package.__path__, package.__name__ + "."
        ):
            short_name = name.rsplit(".", 1)[-1]

            if not ispkg or short_name.startswith("_"):
                continue

            try:
                self._try_register(name, short_name)
            except Exception as exc:
                reason = str(exc)
                self._skipped[short_name] = reason
                logger.warning("Feature '%s' skipped: %s", short_name, reason)

        return self

    def _try_register(self, module_path: str, short_name: str) -> None:
        feature_module = importlib.import_module(module_path)

        meta = getattr(feature_module, "FEATURE_META", None)
        if meta is None:
            raise ValueError(f"No FEATURE_META in {module_path}")

        if not isinstance(meta, FeatureMeta):
            raise TypeError(f"FEATURE_META in {module_path} is not a FeatureMeta instance")

        if not meta.enabled:
            self._skipped[short_name] = "disabled (enabled=False)"
            logger.info("Feature '%s' is disabled, skipping.", short_name)
            return

        if not meta.is_auth_available():
            self._skipped[short_name] = f"missing env var {meta.auth_env_var}"
            logger.warning(
                "Feature '%s' requires %s (not set), skipping.",
                short_name,
                meta.auth_env_var,
            )
            return

        server_module = importlib.import_module(f"{module_path}.server")
        server = getattr(server_module, "mcp", None)

        if server is None:
            raise ValueError(f"No `mcp` object in {module_path}.server")

        self._features[short_name] = RegisteredFeature(
            meta=meta,
            server=server,
            module_path=module_path,
        )
        logger.info("Registered feature '%s' v%s", meta.name, meta.version)

    def mount_all(self, root_server: FastMCP) -> None:
        """Mount all discovered features on the root server."""
        for name, feature in sorted(self._features.items()):
            root_server.mount(feature.server, namespace=name)
            logger.info("Mounted '%s' — %s", name, feature.meta.description)

    def summary(self) -> str:
        """Return a human-readable summary of registered features."""
        lines = [
            f"mcp-sweden — {len(self._features)} feature(s) active, "
            f"{len(self._skipped)} skipped\n"
        ]

        if self._features:
            lines.append("Active:")
            for name, feat in sorted(self._features.items()):
                auth_icon = "🔑" if feat.meta.requires_auth else "🔓"
                lines.append(f"  /{name:<20} {auth_icon} {feat.meta.description}")

        if self._skipped:
            lines.append("\nSkipped:")
            for name, reason in sorted(self._skipped.items()):
                lines.append(f"  {name:<20} ⏭️  {reason}")

        return "\n".join(lines)

    def get_feature(self, name: str) -> RegisteredFeature | None:
        return self._features.get(name)
