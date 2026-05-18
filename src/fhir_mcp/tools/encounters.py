from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool

from fhir_mcp.backend.base import FhirBackend

TOOL_NAME = "fhir_get_encounters"

TOOL_DEF = Tool(
    name=TOOL_NAME,
    description="Get Encounter resources for a patient.",
    inputSchema={
        "type": "object",
        "properties": {"patient_id": {"type": "string"}},
        "required": ["patient_id"],
    },
)


def get_encounters(backend: FhirBackend, patient_id: str) -> list[dict[str, Any]]:
    return backend.search("Encounter", {"patient": patient_id})


def handle(backend: FhirBackend, arguments: dict[str, Any]) -> list[TextContent]:
    return [
        TextContent(
            type="text",
            text=json.dumps(get_encounters(backend, arguments["patient_id"])),
        )
    ]
