"""Pydantic schemas for Begagnad API responses."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Seller:
    """Seller info from a marketplace listing."""

    name: str = ""
    rating: float | None = None


@dataclass
class MarketplaceListing:
    """Unified listing from Blocket or Tradera."""

    id: str = ""
    title: str = ""
    description: str = ""
    price: float | None = None
    currency: str = "SEK"
    location: str = ""
    url: str = ""
    images: list[str] = field(default_factory=list)
    condition: str | None = None
    seller: Seller = field(default_factory=Seller)
    end_date: str | None = None
    source: str = ""
    item_type: str | None = None
