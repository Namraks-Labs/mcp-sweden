"""Pydantic schemas for Riksdag API responses.

API documentation: https://data.riksdagen.se/dokumentation/
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# --- Documents ---


class DocumentHit(BaseModel):
    """A single document from the Riksdag document search."""

    id: str = Field(alias="id")
    doc_id: str = Field(alias="dok_id")
    title: str = Field(alias="titel")
    subtitle: str = Field(default="", alias="undertitel")
    doc_type: str = Field(alias="typ")
    subtype: str = Field(default="", alias="subtyp")
    document_category: str = Field(default="", alias="doktyp")
    date: str = Field(default="", alias="datum")
    session: str = Field(default="", alias="rm")
    organ: str = Field(default="", alias="organ")
    summary: str = Field(default="", alias="summary")
    document_url: str = Field(default="", alias="dokument_url_html")

    model_config = {"populate_by_name": True}


class DocumentListResponse(BaseModel):
    """Response from /dokumentlista/."""

    hits: int = Field(default=0, alias="@traffar")
    documents: list[DocumentHit] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


# --- Members ---


class MemberInfo(BaseModel):
    """A parliament member (ledamot)."""

    person_id: str = Field(alias="intressent_id")
    first_name: str = Field(default="", alias="tilltalsnamn")
    last_name: str = Field(default="", alias="efternamn")
    party: str = Field(default="", alias="parti")
    constituency: str = Field(default="", alias="valkrets")
    status: str = Field(default="", alias="status")
    image_url: str = Field(default="", alias="bild_url_192")

    model_config = {"populate_by_name": True}

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


# --- Votes ---


class VoteSummary(BaseModel):
    """A single vote (votering) from the Riksdag."""

    vote_id: str = Field(alias="votering_id")
    designation: str = Field(default="", alias="beteckning")
    date: str = Field(default="", alias="datum")
    title: str = Field(default="", alias="titel")
    yes_votes: int = Field(default=0, alias="Ja")
    no_votes: int = Field(default=0, alias="Nej")
    abstentions: int = Field(default=0, alias="Avstar")
    absent: int = Field(default=0, alias="Franvarande")
    concern: str = Field(default="", alias="concern")

    model_config = {"populate_by_name": True}


# --- Speeches / Debates ---


class SpeechInfo(BaseModel):
    """A speech (anförande) from a parliamentary debate."""

    speech_id: str = Field(alias="anforande_id")
    speaker: str = Field(default="", alias="talare")
    party: str = Field(default="", alias="parti")
    date: str = Field(default="", alias="datum")
    debate_name: str = Field(default="", alias="avsnittsrubrik")
    text: str = Field(default="", alias="anforandetext")
    doc_id: str = Field(default="", alias="dok_id")
    speaker_id: str = Field(default="", alias="intressent_id")

    model_config = {"populate_by_name": True}
