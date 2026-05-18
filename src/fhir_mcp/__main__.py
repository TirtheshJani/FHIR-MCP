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
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as f:
            return json.load(f)  # type: ignore[no-any-return]
    with path.open("rt") as f:
        return json.load(f)  # type: ignore[no-any-return]


async def _run_stdio(bundle_path: Path) -> None:
    backend = InMemoryBackend.from_bundle(_load_bundle(bundle_path))
    server = create_server(backend=backend)
    async with stdio_server() as (read, write):
        await server.asgi().run(read, write, server.asgi().create_initialization_options())


async def _run_sse(bundle_path: Path, port: int) -> None:
    import uvicorn

    backend = InMemoryBackend.from_bundle(_load_bundle(bundle_path))
    server = create_server(backend=backend)
    config = uvicorn.Config(server.sse_app(), host="0.0.0.0", port=port, log_level="info")
    await uvicorn.Server(config).serve()


def main() -> None:
    from fhir_mcp import __version__

    parser = argparse.ArgumentParser(prog="fhir-mcp")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio")
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.transport == "stdio":
        asyncio.run(_run_stdio(args.bundle))
    elif args.transport == "sse":
        asyncio.run(_run_sse(args.bundle, args.port))


if __name__ == "__main__":
    main()
