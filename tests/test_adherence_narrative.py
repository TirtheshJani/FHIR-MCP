from __future__ import annotations

from typing import Any

from fhir_mcp.adherence.narrative import collect_narrative_resources
from fhir_mcp.backend.in_memory import InMemoryBackend


def test_returns_document_references(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = collect_narrative_resources(backend, patient_id="p1")

    assert result["source"] == "narrative"
    assert result["patient_id"] == "p1"
    assert any(r["resourceType"] == "DocumentReference" for r in result["resources"])
