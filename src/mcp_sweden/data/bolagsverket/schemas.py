"""Pydantic schemas for Bolagsverket API responses.

Models for Swedish company registry data including companies,
officers (board members), and registration events.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompanyAddress(BaseModel):
    """Registered address for a company."""

    street: str = ""
    postal_code: str = ""
    city: str = ""
    municipality: str = ""
    county: str = ""


class Company(BaseModel):
    """Core company information from Bolagsverket."""

    org_number: str = Field(description="Organization number (10 digits, e.g. 5560123456)")
    name: str = Field(description="Registered company name")
    company_type: str = Field(default="", description="Company form (AB, HB, KB, EF, etc.)")
    status: str = Field(default="", description="Registration status (Active, Dissolved, etc.)")
    registration_date: str = Field(default="", description="Date of registration (YYYY-MM-DD)")
    address: CompanyAddress = Field(default_factory=CompanyAddress)
    business_description: str = Field(default="", description="Registered business activity")
    share_capital: str = Field(default="", description="Share capital (for AB)")
    num_employees: str = Field(default="", description="Employee count range")

    def format(self) -> str:
        """Human-readable summary."""
        lines = [
            f"**{self.name}** ({self.org_number})",
            f"Type: {self.company_type}" if self.company_type else "",
            f"Status: {self.status}" if self.status else "",
            f"Registered: {self.registration_date}" if self.registration_date else "",
            f"Activity: {self.business_description}" if self.business_description else "",
            f"Share capital: {self.share_capital}" if self.share_capital else "",
            f"Employees: {self.num_employees}" if self.num_employees else "",
        ]
        addr = self.address
        if addr.street or addr.city:
            addr_str = ", ".join(filter(None, [addr.street, addr.postal_code, addr.city]))
            lines.append(f"Address: {addr_str}")
        return "\n".join(line for line in lines if line)


class CompanyOfficer(BaseModel):
    """Board member, CEO, or other company officer."""

    name: str = Field(description="Full name")
    role: str = Field(description="Role (Styrelseledamot, VD, Ordförande, etc.)")
    personal_number_last4: str = Field(
        default="", description="Last 4 digits of personal number (if public)"
    )
    appointed_date: str = Field(default="", description="Date appointed (YYYY-MM-DD)")

    def format(self) -> str:
        lines = [f"- **{self.name}** — {self.role}"]
        if self.appointed_date:
            lines[0] += f" (since {self.appointed_date})"
        return lines[0]


class CompanyEvent(BaseModel):
    """Registration event or change for a company."""

    date: str = Field(description="Event date (YYYY-MM-DD)")
    event_type: str = Field(description="Type of registration event")
    description: str = Field(default="", description="Event description")

    def format(self) -> str:
        return f"- {self.date}: {self.event_type}" + (
            f" — {self.description}" if self.description else ""
        )


class CompanySearchResult(BaseModel):
    """Wrapper for search results."""

    companies: list[Company] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    query: str = ""

    def format(self) -> str:
        if not self.companies:
            return f'No companies found for "{self.query}".'
        header = f'Found {self.total_count} companies for "{self.query}" (page {self.page}):\n'
        items = [
            f"{i + 1}. {c.name} ({c.org_number}) — {c.company_type}"
            for i, c in enumerate(self.companies)
        ]
        return header + "\n".join(items)
