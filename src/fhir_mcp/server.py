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
        from fhir_mcp.tools import patients

        self._tools.append(patients.TOOL_DEF)
        self._handlers[patients.TOOL_NAME] = patients.handle

        # Register list_tools and call_tool handlers
        self._update_tool_registration()
        self._update_call_handler()

    def _update_tool_registration(self) -> None:
        """Re-register list_tools after adding more tools."""
        tools_snapshot = list(self._tools)

        @self._mcp.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
        async def _list_tools() -> list[Tool]:
            return tools_snapshot

    def _update_call_handler(self) -> None:
        """Re-register call_tool dispatch handler."""
        backend = self._backend
        handlers = self._handlers

        @self._mcp.call_tool()  # type: ignore[untyped-decorator]
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


def create_server(backend: Any) -> FhirMcpServer:
    return FhirMcpServer(backend)
