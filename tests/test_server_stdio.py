from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_create_server_registers_tools() -> None:
    from fhir_mcp.server import create_server

    backend_stub = object()
    server = create_server(backend=backend_stub)

    tool_names = await server.list_tool_names()
    assert "fhir_search_patients" in tool_names


@pytest.mark.asyncio
async def test_search_patients_round_trip_returns_results() -> None:
    fixture = Path(__file__).parent / "fixtures" / "mini_bundle.json"
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "fhir_mcp", "--bundle", str(fixture)],
    )
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("fhir_search_patients", {"criteria": {}})

    payload = json.loads(result.content[0].text)
    assert {p["id"] for p in payload} == {"p1", "p2", "p3"}
