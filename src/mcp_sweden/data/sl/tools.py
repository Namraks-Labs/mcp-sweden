"""Tool implementations for the SL feature.

Each function becomes an MCP tool registered in server.py.
"""

from __future__ import annotations

import logging

from . import client

logger = logging.getLogger(__name__)


async def search_stations(query: str) -> str:
    """Search for SL stations/stops in Stockholm by name.

    Args:
        query: Station name to search for (e.g. 'T-Centralen', 'Slussen',
               'Odenplan'). Case-insensitive substring match.

    Returns:
        List of matching stations with IDs, names, and coordinates.
        Use the station ID with get_departures to see real-time departures.
    """
    sites = await client.search_sites(query)

    if not sites:
        return f"No stations found matching '{query}'."

    # Cap results
    total = len(sites)
    sites = sites[:25]

    lines = [f"Found {total} station(s) matching '{query}'"]
    if total > 25:
        lines[0] += " (showing first 25)"
    lines[0] += ":\n"

    for s in sites:
        name = s.get("name", "Unknown")
        site_id = s.get("id", "?")
        note = s.get("note", "")
        lat = s.get("lat", "")
        lon = s.get("lon", "")

        line = f"- {name} (ID: {site_id})"
        if note:
            line += f" — {note}"
        if lat and lon:
            line += f" [{lat:.4f}, {lon:.4f}]"
        lines.append(line)

    return "\n".join(lines)


async def get_departures(
    station_id: int,
    transport_mode: str = "",
    line: str = "",
    direction: int = 0,
) -> str:
    """Get real-time departures from an SL station in Stockholm.

    Args:
        station_id: Station ID (get this from search_stations).
                    Common IDs: 9001 (T-Centralen), 9192 (Slussen),
                    9117 (Odenplan), 9180 (Stockholms central/pendeltåg).
        transport_mode: Filter by transport type — 'METRO', 'BUS', 'TRAM',
                       'TRAIN', 'SHIP', 'FERRY'. Leave empty for all.
        line: Filter by line number (e.g. '10', '172', '7').
        direction: Direction filter (1 or 2). 0 = both directions.

    Returns:
        Real-time departure board with line, destination, and expected time.
    """
    data = await client.get_departures(
        site_id=station_id,
        transport_mode=transport_mode,
        direction=direction,
        line=line,
    )

    departures = data.get("departures", [])
    if not departures:
        mode_info = f" ({transport_mode})" if transport_mode else ""
        return f"No departures found for station {station_id}{mode_info}."

    # Group by stop area for clarity
    stop_name = departures[0].get("stop_area", {}).get("name", f"Station {station_id}")

    # Cap at 30 departures
    shown = departures[:30]

    lines_out = [f"Departures from {stop_name}:\n"]

    for dep in shown:
        line_info = dep.get("line", {})
        line_designation = line_info.get("designation", "?")
        mode = line_info.get("transport_mode", "")
        destination = dep.get("destination", "Unknown")
        display = dep.get("display", "")
        scheduled = dep.get("scheduled", "")
        expected = dep.get("expected", "")
        state = dep.get("state", "")
        stop_point = dep.get("stop_point", {})
        platform = stop_point.get("designation", "")

        # Format time display
        time_str = display
        if not time_str and expected:
            time_str = expected.split("T")[1][:5] if "T" in expected else expected

        # Mode emoji
        mode_icon = {
            "METRO": "M",
            "BUS": "B",
            "TRAM": "T",
            "TRAIN": "J",
            "SHIP": "S",
            "FERRY": "F",
        }.get(mode, "?")

        entry = f"  [{mode_icon}] Line {line_designation} → {destination}"
        if time_str:
            entry += f"  |  {time_str}"
        if platform:
            entry += f"  |  Platform {platform}"

        # Add delay info
        if scheduled and expected and scheduled != expected:
            sched_time = scheduled.split("T")[1][:5] if "T" in scheduled else ""
            if sched_time:
                entry += f"  (scheduled {sched_time})"

        if state == "CANCELLED":
            entry += "  [CANCELLED]"

        # Deviations
        deviations = dep.get("deviations", [])
        for dev in deviations:
            msg = dev.get("message", "")
            if msg:
                entry += f"\n      ⚠ {msg}"

        lines_out.append(entry)

    remaining = len(departures) - len(shown)
    if remaining > 0:
        lines_out.append(f"\n  ... and {remaining} more departures")

    return "\n".join(lines_out)


async def list_lines(transport_mode: str = "") -> str:
    """List all SL transport lines in Stockholm.

    Args:
        transport_mode: Filter by type — 'metro', 'bus', 'tram', 'train',
                       'ship', 'ferry'. Leave empty for all modes.

    Returns:
        All SL lines grouped by transport mode with line numbers and names.
    """
    all_lines = await client.list_lines()

    if not all_lines:
        return "No line data available."

    # Filter by mode if specified
    if transport_mode:
        key = transport_mode.lower()
        if key in all_lines:
            all_lines = {key: all_lines[key]}
        else:
            return (
                f"Unknown transport mode '{transport_mode}'. "
                f"Valid modes: {', '.join(all_lines.keys())}"
            )

    lines_out = ["SL Lines:\n"]

    for mode, mode_lines in all_lines.items():
        if not mode_lines:
            continue

        mode_label = mode.upper()
        lines_out.append(f"  {mode_label} ({len(mode_lines)} lines):")

        for ml in mode_lines:
            designation = ml.get("designation", "?")
            name = ml.get("name", "")
            group = ml.get("group_of_lines", "")

            entry = f"    Line {designation}"
            if name:
                entry += f" — {name}"
            elif group:
                entry += f" — {group}"
            lines_out.append(entry)

        lines_out.append("")

    return "\n".join(lines_out)


async def get_station_info(station_id: int) -> str:
    """Get detailed information about a specific SL station.

    Args:
        station_id: Station ID (get this from search_stations).

    Returns:
        Station details including name, location, and available transport modes
        based on current departures.
    """
    # Get station details from the sites list
    sites = await client.list_sites()
    station = next((s for s in sites if s.get("id") == station_id), None)

    if not station:
        return f"No station found with ID {station_id}."

    name = station.get("name", "Unknown")
    note = station.get("note", "")
    lat = station.get("lat", "")
    lon = station.get("lon", "")

    lines_out = [f"Station: {name} (ID: {station_id})"]
    if note:
        lines_out.append(f"Area: {note}")
    if lat and lon:
        lines_out.append(f"Coordinates: {lat:.6f}, {lon:.6f}")

    # Get current departures to determine available modes and lines
    data = await client.get_departures(site_id=station_id)
    departures = data.get("departures", [])

    if departures:
        # Collect unique modes and lines
        modes: set[str] = set()
        line_set: set[str] = set()
        destinations: set[str] = set()

        for dep in departures:
            line_info = dep.get("line", {})
            mode = line_info.get("transport_mode", "")
            designation = line_info.get("designation", "")
            group = line_info.get("group_of_lines", "")
            dest = dep.get("destination", "")

            if mode:
                modes.add(mode)
            if designation:
                label = f"Line {designation}"
                if group:
                    label += f" ({group})"
                line_set.add(label)
            if dest:
                destinations.add(dest)

        if modes:
            lines_out.append(f"\nTransport modes: {', '.join(sorted(modes))}")
        if line_set:
            lines_out.append("\nLines serving this station:")
            for ln in sorted(line_set):
                lines_out.append(f"  - {ln}")
        if destinations:
            lines_out.append("\nDestinations:")
            for d in sorted(destinations):
                lines_out.append(f"  - {d}")
    else:
        lines_out.append("\nNo current departures (station may be closed or inactive).")

    return "\n".join(lines_out)


async def get_nearby_stations(
    latitude: float,
    longitude: float,
    radius_km: float = 1.0,
) -> str:
    """Find SL stations near a given location in Stockholm.

    Args:
        latitude: Latitude coordinate (e.g. 59.3293 for Stockholm city center).
        longitude: Longitude coordinate (e.g. 18.0686 for Stockholm city center).
        radius_km: Search radius in kilometers (default 1.0, max 5.0).

    Returns:
        Nearby stations sorted by distance, with IDs for use with get_departures.
    """
    radius = min(radius_km, 5.0)
    nearby = await client.get_nearby_sites(latitude, longitude, radius_km=radius)

    if not nearby:
        return f"No stations found within {radius} km of ({latitude}, {longitude})."

    # Cap results
    total = len(nearby)
    nearby = nearby[:20]

    lines_out = [f"Found {total} station(s) within {radius} km"]
    if total > 20:
        lines_out[0] += " (showing nearest 20)"
    lines_out[0] += ":\n"

    for s in nearby:
        name = s.get("name", "Unknown")
        site_id = s.get("id", "?")
        distance = s.get("_distance_km", "?")
        note = s.get("note", "")

        entry = f"  - {name} (ID: {site_id}) — {distance} km"
        if note:
            entry += f" [{note}]"
        lines_out.append(entry)

    return "\n".join(lines_out)
