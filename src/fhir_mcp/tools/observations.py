from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool

from fhir_mcp.backend.base import FhirBackend

TOOL_NAME = "fhir_get_observations"

TOOL_DEF = Tool(
    name=TOOL_NAME,
    description="Get Observation resources for a patient, optionally filtered by code.",
    inputSchema={
        "type": "object",
        "properties": {
            "patient_id": {"type": "string"},
            "code": {"type": "string"},
        },
        "required": ["patient_id"],
    },
)


def get_observations(
    backend: FhirBackend,
    patient_id: str,
    code: str | None,
) -> list[dict[str, Any]]:
    results = backend.search("Observation", {"patient": patient_id})
    if code:
        results = [
            o
            for o in results
            if any(c.get("code") == code for c in o.get("code", {}).get("coding", []))
        ]
    return results


def handle(backend: FhirBackend, arguments: dict[str, Any]) -> list[TextContent]:
    results = get_observations(
        backend,
        patient_id=arguments["patient_id"],
        code=arguments.get("code"),
    )
    return [TextContent(type="text", text=json.dumps(results))]
