from __future__ import annotations

import argparse
import asyncio
import gzip
import json
from pathlib import Path

from mcp.server.stdio import stdio_server

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.server import create_server


def _load_bundle(path: Path) -> dict[str, object]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        return json.load(f)  # type: ignore[no-any-return]


async def _run_stdio(bundle_path: Path) -> None:
    backend = InMemoryBackend.from_bundle(_load_bundle(bundle_path))
    server = create_server(backend=backend)
    async with stdio_server() as (read, write):
        await server.asgi().run(read, write, server.asgi().create_initialization_options())


def main() -> None:
    parser = argparse.ArgumentParser(prog="fhir-mcp")
    parser.add_argument("--transport", choices=["stdio"], default="stdio")
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    if args.transport == "stdio":
        asyncio.run(_run_stdio(args.bundle))


if __name__ == "__main__":
    main()
