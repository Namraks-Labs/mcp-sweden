"""Tool implementations for the Riksdag feature.

Each function becomes an MCP tool registered in server.py.
"""

from __future__ import annotations

import logging
import re

from . import client

logger = logging.getLogger(__name__)


def _strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", text).strip()


def _truncate(text: str, max_len: int = 500) -> str:
    """Truncate text to max_len characters."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


async def search_documents(
    query: str = "",
    doc_type: str = "",
    session: str = "",
    organ: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 10,
) -> str:
    """Search Swedish parliament (Riksdag) documents — motions, propositions, reports, etc.

    Args:
        query: Free text search term.
        doc_type: Document type — 'mot' (motion), 'prop' (proposition),
                  'bet' (committee report), 'sou' (government inquiry),
                  'ds' (ministry report). Leave empty for all types.
        session: Parliamentary session, e.g. '2024/25'.
        organ: Committee code, e.g. 'FiU' (Finance), 'JuU' (Justice).
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (starts at 1).
        page_size: Results per page (max 20).

    Returns:
        Formatted list of matching documents with titles, dates, and URLs.
    """
    raw = await client.search_documents(
        query=query,
        doc_type=doc_type,
        session=session,
        organ=organ,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=min(page_size, 20),
    )

    doc_list = raw.get("dokumentlista", {})
    total = doc_list.get("@traffar", "0")
    docs = doc_list.get("dokument", [])

    if not docs:
        return f"No documents found (total matches: {total})."

    if isinstance(docs, dict):
        docs = [docs]

    lines = [f"Found {total} documents (showing page {page}):\n"]
    for doc in docs:
        title = doc.get("titel", "Untitled")
        doc_id = doc.get("dok_id", "")
        date = doc.get("datum", "")
        dtype = doc.get("doktyp", "")
        organ_name = doc.get("organ", "")
        summary = _strip_html(doc.get("summary", ""))
        url = doc.get("dokument_url_html", "")

        line = f"• [{dtype}] {title}"
        if doc_id:
            line += f" ({doc_id})"
        if date:
            line += f" — {date}"
        if organ_name:
            line += f" [{organ_name}]"
        if summary:
            line += f"\n  {_truncate(summary, 200)}"
        if url:
            line += f"\n  {url}"
        lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------


async def list_members(
    party: str = "",
    constituency: str = "",
) -> str:
    """List current Swedish parliament (Riksdag) members.

    Args:
        party: Filter by party abbreviation — S (Social Democrats),
               M (Moderates), SD (Sweden Democrats), C (Centre),
               V (Left), KD (Christian Democrats), L (Liberals),
               MP (Green Party).
        constituency: Filter by constituency (valkrets), e.g. 'Stockholms kommun'.

    Returns:
        List of members with name, party, and constituency.
    """
    raw = await client.list_members(party=party, constituency=constituency)

    person_list = raw.get("personlista", {})
    persons = person_list.get("person", [])

    if not persons:
        return "No members found matching the criteria."

    if isinstance(persons, dict):
        persons = [persons]

    lines = [f"Found {len(persons)} member(s):\n"]
    for p in persons:
        name = f"{p.get('tilltalsnamn', '')} {p.get('efternamn', '')}".strip()
        party_name = p.get("parti", "")
        valkrets = p.get("valkrets", "")
        status = p.get("status", "")

        line = f"• {name} ({party_name})"
        if valkrets:
            line += f" — {valkrets}"
        if status:
            line += f" [{status}]"
        lines.append(line)

    return "\n".join(lines)


async def get_member_details(person_id: str) -> str:
    """Get detailed information about a specific parliament member.

    Args:
        person_id: The member's unique ID (intressent_id).
                   Get this from list_members results.

    Returns:
        Detailed member profile including roles and assignments.
    """
    raw = await client.get_member(person_id)

    person = raw.get("person", raw.get("personlista", {}).get("person", {}))
    if isinstance(person, list):
        person = person[0] if person else {}

    if not person:
        return f"No member found with ID: {person_id}"

    name = f"{person.get('tilltalsnamn', '')} {person.get('efternamn', '')}".strip()
    party = person.get("parti", "")
    constituency = person.get("valkrets", "")
    born = person.get("fodd_ar", "")
    status = person.get("status", "")

    lines = [f"**{name}** ({party})"]
    if constituency:
        lines.append(f"Constituency: {constituency}")
    if born:
        lines.append(f"Born: {born}")
    if status:
        lines.append(f"Status: {status}")

    # Assignments/roles
    assignments = person.get("personuppdrag", {}).get("uppdrag", [])
    if isinstance(assignments, dict):
        assignments = [assignments]
    if assignments:
        current = [a for a in assignments if a.get("tom", "") == ""]
        if current:
            lines.append("\nCurrent roles:")
            for a in current[:10]:
                role = a.get("roll_kod", "")
                organ = a.get("organ_kod", "")
                task = a.get("uppgift", "")
                line = f"  • {role}"
                if organ:
                    line += f" — {organ}"
                if task:
                    line += f": {task}"
                lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Votes
# ---------------------------------------------------------------------------


async def search_votes(
    session: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 10,
) -> str:
    """Search parliamentary votes in the Swedish Riksdag.

    Args:
        session: Parliamentary session, e.g. '2024/25'.
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (starts at 1).
        page_size: Results per page (max 20).

    Returns:
        List of votes with results (yes/no/abstain/absent counts).
    """
    raw = await client.search_votes(
        session=session,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=min(page_size, 20),
    )

    vote_list = raw.get("voteringlista", {})
    total = vote_list.get("@traffar", "0")
    votes = vote_list.get("votering", [])

    if not votes:
        return f"No votes found (total: {total})."

    if isinstance(votes, dict):
        votes = [votes]

    lines = [f"Found {total} votes (showing page {page}):\n"]
    for v in votes:
        designation = v.get("beteckning", "")
        date = v.get("datum", "")
        title = v.get("titel", v.get("punkt", ""))
        yes = v.get("Ja", "?")
        no = v.get("Nej", "?")
        abstain = v.get("Avstar", "?")
        absent = v.get("Franvarande", "?")

        line = f"• {designation}"
        if title:
            line += f": {_truncate(title, 100)}"
        if date:
            line += f" — {date}"
        line += f"\n  Yes: {yes} | No: {no} | Abstain: {abstain} | Absent: {absent}"
        lines.append(line)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Speeches / Debates
# ---------------------------------------------------------------------------


async def search_speeches(
    query: str = "",
    party: str = "",
    from_date: str = "",
    to_date: str = "",
    page: int = 1,
    page_size: int = 10,
) -> str:
    """Search parliamentary speeches and debate contributions in the Riksdag.

    Args:
        query: Free text search in speech content.
        party: Filter by party abbreviation (S, M, SD, etc.).
        from_date: Start date (YYYY-MM-DD).
        to_date: End date (YYYY-MM-DD).
        page: Page number (starts at 1).
        page_size: Results per page (max 20).

    Returns:
        List of speeches with speaker, date, and excerpt.
    """
    raw = await client.search_speeches(
        query=query,
        party=party,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=min(page_size, 20),
    )

    speech_list = raw.get("anforandelista", {})
    total = speech_list.get("@traffar", "0")
    speeches = speech_list.get("anforande", [])

    if not speeches:
        return f"No speeches found (total: {total})."

    if isinstance(speeches, dict):
        speeches = [speeches]

    lines = [f"Found {total} speeches (showing page {page}):\n"]
    for s in speeches:
        speaker = s.get("talare", "Unknown")
        party_name = s.get("parti", "")
        date = s.get("datum", "")
        topic = s.get("avsnittsrubrik", "")
        text = _strip_html(s.get("anforandetext", ""))

        line = f"• {speaker}"
        if party_name:
            line += f" ({party_name})"
        if date:
            line += f" — {date}"
        if topic:
            line += f"\n  Topic: {topic}"
        if text:
            line += f"\n  {_truncate(text, 200)}"
        lines.append(line)

    return "\n".join(lines)
