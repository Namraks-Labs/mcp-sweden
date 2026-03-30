"""Tests for the Sveriges Radio feature.

Uses live API calls — the SR API is free, public, and rate-limit-friendly.
"""

from __future__ import annotations

import json

import pytest

from mcp_sweden.data.sverigesradio import tools


@pytest.mark.asyncio
async def test_list_channels():
    result = json.loads(await tools.list_channels())
    assert "channels" in result
    assert result["count"] > 0
    ch = result["channels"][0]
    assert "id" in ch
    assert "name" in ch


@pytest.mark.asyncio
async def test_get_schedule():
    # P1 = channel 132
    result = json.loads(await tools.get_schedule(channel_id=132))
    assert "schedule" in result
    assert len(result["schedule"]) > 0
    ep = result["schedule"][0]
    assert "title" in ep
    assert "start_time" in ep


@pytest.mark.asyncio
async def test_search_programs():
    result = json.loads(await tools.search_programs(query="Ekot"))
    assert "programs" in result
    assert result["total"] > 0
    p = result["programs"][0]
    assert "id" in p
    assert "name" in p


@pytest.mark.asyncio
async def test_search_programs_by_channel():
    # P1 = channel 132
    result = json.loads(await tools.search_programs(channel_id=132))
    assert "programs" in result
    assert result["total"] > 0


@pytest.mark.asyncio
async def test_get_episodes():
    # Ekot = program 4540
    result = json.loads(await tools.get_episodes(program_id=4540))
    assert "episodes" in result
    assert len(result["episodes"]) > 0
    ep = result["episodes"][0]
    assert "id" in ep
    assert "title" in ep


@pytest.mark.asyncio
async def test_get_latest_episode():
    result = json.loads(await tools.get_latest_episode(program_id=4540))
    assert "id" in result
    assert "title" in result


@pytest.mark.asyncio
async def test_get_now_playing():
    # P3 = channel 164
    result = json.loads(await tools.get_now_playing(channel_id=164))
    assert "channel" in result
    assert "channel_id" in result


@pytest.mark.asyncio
async def test_get_traffic_messages():
    result = json.loads(await tools.get_traffic_messages())
    # May or may not have messages, but structure should be valid
    assert "area" in result


@pytest.mark.asyncio
async def test_list_traffic_areas():
    result = json.loads(await tools.list_traffic_areas())
    assert "areas" in result
    assert result["count"] > 0
