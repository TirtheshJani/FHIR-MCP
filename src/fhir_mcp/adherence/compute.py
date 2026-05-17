from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool

from fhir_mcp.adherence.narrative import collect_narrative_resources
from fhir_mcp.adherence.routing import HeuristicRouter, Intent, Router
from fhir_mcp.adherence.structured import compute_structured_adherence
from fhir_mcp.backend.base import FhirBackend

TOOL_NAME = "compute_adherence"

TOOL_DEF = Tool(
    name=TOOL_NAME,
    description=(
        "Composite tool that routes adherence questions. Structured intent "
        "computes a dose-count ratio over MedicationRequest/Observation. "
        "Narrative intent returns DocumentReference resources for the agent "
        "to summarize. Routing rule justified by Jani et al., May 2026 "
        "preprint (structured AUC 0.997, narrative AUC 0.843)."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "patient_id": {"type": "string"},
            "medication": {"type": "string"},
            "question": {"type": "string"},
        },
        "required": ["patient_id", "medication", "question"],
    },
)

_DEFAULT_ROUTER: Router = HeuristicRouter()


def compute_adherence(
    backend: FhirBackend,
    patient_id: str,
    medication: str,
    question: str,
    router: Router | None = None,
) -> dict[str, Any]:
    router = router or _DEFAULT_ROUTER
    intent = router.detect(question)

    if intent is Intent.STRUCTURED:
        return {
            "branch": "structured",
            "structured": compute_structured_adherence(backend, patient_id, medication),
        }
    if intent is Intent.NARRATIVE:
        return {
            "branch": "narrative",
            "narrative": collect_narrative_resources(backend, patient_id),
        }
    return {
        "branch": "ambiguous",
        "structured": compute_structured_adherence(backend, patient_id, medication),
        "narrative": collect_narrative_resources(backend, patient_id),
    }


def handle(backend: FhirBackend, arguments: dict[str, Any]) -> list[TextContent]:
    result = compute_adherence(
        backend,
        patient_id=arguments["patient_id"],
        medication=arguments["medication"],
        question=arguments["question"],
    )
    return [TextContent(type="text", text=json.dumps(result))]
