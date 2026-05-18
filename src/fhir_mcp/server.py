from __future__ import annotations

from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool


class FhirMcpServer:
    def __init__(self, backend: Any) -> None:
        self._mcp = Server("fhir-mcp")
        self._backend = backend
        self._tools: list[Tool] = []
        self._handlers: dict[str, Any] = {}
        self._register_tools()

    def _register_tools(self) -> None:
        from fhir_mcp.adherence import compute as compute_adherence_mod
        from fhir_mcp.tools import conditions, encounters, medications, observations, patients

        all_tool_mods = (
            patients,
            observations,
            medications,
            conditions,
            encounters,
            compute_adherence_mod,
        )
        for tool_mod in all_tool_mods:
            self._tools.append(tool_mod.TOOL_DEF)
            self._handlers[tool_mod.TOOL_NAME] = tool_mod.handle

        # Register list_tools and call_tool handlers
        self._update_tool_registration()
        self._update_call_handler()

    def _update_tool_registration(self) -> None:
        """Re-register list_tools after adding more tools."""
        tools_snapshot = list(self._tools)

        @self._mcp.list_tools()  # type: ignore[misc]
        async def _list_tools() -> list[Tool]:
            return tools_snapshot

    def _update_call_handler(self) -> None:
        """Re-register call_tool dispatch handler."""
        backend = self._backend
        handlers = self._handlers

        @self._mcp.call_tool()  # type: ignore[misc]
        async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            if name not in handlers:
                raise ValueError(f"unknown tool: {name}")
            return handlers[name](backend, arguments)  # type: ignore[no-any-return]

    def add_tool(self, tool_def: Tool, handler: Any) -> None:
        self._tools.append(tool_def)
        self._handlers[tool_def.name] = handler
        self._update_tool_registration()

    async def list_tool_names(self) -> list[str]:
        return [t.name for t in self._tools]

    def asgi(self) -> Server:
        return self._mcp

    def sse_app(self) -> Any:
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        transport = SseServerTransport("/messages/")
        mcp_server = self._mcp

        async def handle_sse(scope: Any, receive: Any, send: Any) -> None:
            async with transport.connect_sse(scope, receive, send) as (read, write):
                await mcp_server.run(read, write, mcp_server.create_initialization_options())

        return Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages", app=transport.handle_post_message),
            ]
        )


def create_server(backend: Any) -> FhirMcpServer:
    return FhirMcpServer(backend)
