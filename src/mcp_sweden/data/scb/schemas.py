"""Pydantic schemas for SCB API responses.

SCB Statistical Database API returns two main structures:
1. Navigation nodes (folders/tables in the hierarchy)
2. Query results (JSON-stat2 format)
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- Navigation / Table Metadata ---


class TableNode(BaseModel):
    """A node in the SCB table hierarchy (folder or table)."""

    id: str = ""
    type: str = ""  # "l" = folder, "t" = table
    text: str = ""
    updated: str | None = None


class VariableValue(BaseModel):
    """A selectable value within a variable."""

    code: str = Field(alias="code", default="")
    text: str = Field(alias="text", default="")

    model_config = {"populate_by_name": True}


class Variable(BaseModel):
    """A variable (dimension) in an SCB table."""

    code: str = ""
    text: str = ""
    values: list[str] = Field(default_factory=list)
    valueTexts: list[str] = Field(default_factory=list)
    elimination: bool = False
    time: bool = False


class TableMetadata(BaseModel):
    """Full metadata for an SCB table, including its variables."""

    title: str = ""
    variables: list[Variable] = Field(default_factory=list)


# --- Query Request ---


class VariableSelection(BaseModel):
    """Selection filter for a single variable in a query."""

    filter: str = "item"  # "item", "vs:RegionKommun08", "all", "top", etc.
    values: list[str] = Field(default_factory=list)


class QueryVariable(BaseModel):
    """A variable with its selection in a query request."""

    code: str
    selection: VariableSelection


class QueryRequest(BaseModel):
    """Request body for querying SCB data."""

    query: list[QueryVariable] = Field(default_factory=list)
    response: dict[str, str] = Field(default_factory=lambda: {"format": "json"})


# --- Query Response (SCB JSON format) ---


class ResponseColumn(BaseModel):
    """Column definition in SCB JSON response."""

    code: str = ""
    text: str = ""
    type: str = ""  # "d" = dimension, "c" = data


class ResponseRow(BaseModel):
    """A row of data in SCB JSON response."""

    key: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """Full query response from SCB API."""

    columns: list[ResponseColumn] = Field(default_factory=list)
    comments: list[dict[str, str]] = Field(default_factory=list)
    data: list[ResponseRow] = Field(default_factory=list)
