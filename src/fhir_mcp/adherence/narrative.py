from __future__ import annotations

from typing import Any

from fhir_mcp.backend.base import FhirBackend


def collect_narrative_resources(backend: FhirBackend, patient_id: str) -> dict[str, Any]:
    docs = backend.search("DocumentReference", {"patient": patient_id})
    compositions = backend.search("Composition", {"patient": patient_id})
    return {
        "source": "narrative",
        "patient_id": patient_id,
        "resources": docs + compositions,
        "note": (
            "Narrative resources returned as-is. The calling agent should "
            "summarize them. Per the May 2026 preprint (Jani et al.), "
            "narrative-RAG outperforms structured FHIR on free-form questions "
            "at AUC 0.843."
        ),
    }
