"""Pydantic schemas for Skolverket API responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- School Registry API (skolenhetsregistret/v1) ---


class GeoData(BaseModel):
    """Geographic coordinates for a school."""

    lat: str | None = Field(None, alias="Koordinat_WGS84_Lat")
    lng: str | None = Field(None, alias="Koordinat_WGS84_Lng")

    model_config = {"populate_by_name": True}


class Address(BaseModel):
    """Physical address."""

    street: str | None = Field(None, alias="Adress")
    zip_code: str | None = Field(None, alias="Postnr")
    city: str | None = Field(None, alias="Ort")
    geo: GeoData | None = Field(None, alias="GeoData")

    model_config = {"populate_by_name": True}


class SchoolForm(BaseModel):
    """Type of education offered by a school unit."""

    name: str = Field(alias="Benamning")
    form_id: int = Field(alias="SkolformID")
    form_code: str = Field(alias="SkolformKod")

    model_config = {"populate_by_name": True}


class Municipality(BaseModel):
    """Municipality reference."""

    code: str = Field(alias="Kommunkod")
    name: str = Field(alias="Namn")

    model_config = {"populate_by_name": True}


class Principal(BaseModel):
    """School principal organizer (huvudman)."""

    org_nr: str = Field(alias="PeOrgNr")
    name: str = Field(alias="Namn")
    type: str = Field(alias="Typ")

    model_config = {"populate_by_name": True}


class SchoolUnitDetail(BaseModel):
    """Detailed school unit from the registry API."""

    name: str = Field(alias="Namn")
    code: str = Field(alias="Skolenhetskod")
    principal_name: str | None = Field(None, alias="Rektorsnamn")
    email: str | None = Field(None, alias="Epost")
    phone: str | None = Field(None, alias="Telefon")
    website: str | None = Field(None, alias="Webbadress")
    visit_address: Address | None = Field(None, alias="Besoksadress")
    school_forms: list[SchoolForm] = Field(default_factory=list, alias="Skolformer")
    municipality: Municipality | None = Field(None, alias="Kommun")
    principal: Principal | None = Field(None, alias="Huvudman")
    status: str = Field(alias="Status")
    start_date: str | None = Field(None, alias="Startdatum")

    model_config = {"populate_by_name": True}


class SchoolUnitListItem(BaseModel):
    """Brief school unit entry from the registry list API."""

    code: str = Field(alias="Skolenhetskod")
    municipality_code: str = Field(alias="Kommunkod")
    org_nr: str = Field(alias="PeOrgNr")
    name: str = Field(alias="Skolenhetsnamn")
    status: str = Field(alias="Status")

    model_config = {"populate_by_name": True}


# --- Planned Educations API (planned-educations/v3) ---


class SchoolingType(BaseModel):
    """Type of schooling with year range."""

    code: str
    display_name: str = Field(alias="displayName")
    school_years: list[str] = Field(default_factory=list, alias="schoolYears")

    model_config = {"populate_by_name": True}


class PlannedSchoolUnit(BaseModel):
    """School unit from the planned-educations API."""

    code: str
    name: str
    municipality_code: str = Field(alias="geographicalAreaCode")
    post_code_district: str | None = Field(None, alias="postCodeDistrict")
    type_of_schooling: list[SchoolingType] = Field(
        default_factory=list, alias="typeOfSchooling"
    )
    students_per_teacher: str | None = Field(None, alias="studentsPerTeacherQuota")
    principal_type: str | None = Field(None, alias="principalOrganizerType")

    model_config = {"populate_by_name": True}


class StatisticValue(BaseModel):
    """A single statistic data point."""

    value: str
    value_type: str = Field(alias="valueType")
    time_period: str = Field(alias="timePeriod")

    model_config = {"populate_by_name": True}
