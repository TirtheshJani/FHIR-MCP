from __future__ import annotations

import asyncio
import json
import socket
from pathlib import Path

import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.sse import sse_client

from fhir_mcp.__main__ import _load_bundle
from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.server import create_server


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.mark.asyncio
async def test_sse_round_trip_returns_results() -> None:
    fixture = Path(__file__).parent / "fixtures" / "mini_bundle.json"
    backend = InMemoryBackend.from_bundle(_load_bundle(fixture))
    app = create_server(backend=backend).sse_app()
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    task = asyncio.create_task(server.serve())
    try:
        while not server.started:
            await asyncio.sleep(0.05)
        url = f"http://127.0.0.1:{port}/sse"
        async with sse_client(url) as (read, write), ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("fhir_search_patients", {"criteria": {}})
        payload = json.loads(result.content[0].text)
        assert {p["id"] for p in payload} == {"p1", "p2", "p3"}
    finally:
        server.should_exit = True
        await task
