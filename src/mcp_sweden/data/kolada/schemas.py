"""Pydantic schemas for Kolada API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field


class KpiInfo(BaseModel):
    """A key performance indicator definition."""

    id: str
    title: str = ""
    description: str = ""
    operating_area: str = ""
    has_ou_data: bool = False
    is_divided_by_gender: int = 0
    municipality_type: str = ""
    prel_publication_date: str = ""
    publication_date: str = ""


class KpiSearchResponse(BaseModel):
    """Response from KPI search/list."""

    count: int = 0
    values: list[KpiInfo] = Field(default_factory=list)


class MunicipalityInfo(BaseModel):
    """A municipality or region."""

    id: str
    title: str = ""
    type: str = ""  # "K" = kommun, "L" = landsting/region


class MunicipalityResponse(BaseModel):
    """Response from municipality listing."""

    count: int = 0
    values: list[MunicipalityInfo] = Field(default_factory=list)


class DataValue(BaseModel):
    """A single data point from Kolada."""

    kpi: str = ""
    municipality: str = ""
    period: str = ""
    gender: str = ""
    status: str = ""
    value: float | None = None
    count: int | None = None


class DataPeriod(BaseModel):
    """Data grouped by period."""

    period: str = ""
    values: list[DataValue] = Field(default_factory=list)


class DataResponse(BaseModel):
    """Response from data queries."""

    count: int = 0
    values: list[DataPeriod] = Field(default_factory=list)
