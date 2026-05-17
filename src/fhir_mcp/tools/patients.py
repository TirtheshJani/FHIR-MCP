from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool

from fhir_mcp.backend.base import FhirBackend  # noqa: F401 (used for type hints)

TOOL_NAME = "fhir_search_patients"

TOOL_DEF = Tool(
    name=TOOL_NAME,
    description="Search Patient resources by criteria. Empty criteria returns all.",
    inputSchema={
        "type": "object",
        "properties": {"criteria": {"type": "object", "additionalProperties": {"type": "string"}}},
        "required": ["criteria"],
    },
)


def handle(backend: FhirBackend, arguments: dict[str, Any]) -> list[TextContent]:
    results = backend.search("Patient", arguments.get("criteria", {}))
    return [TextContent(type="text", text=json.dumps(results))]
