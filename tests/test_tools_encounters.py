from __future__ import annotations

from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.tools.encounters import get_encounters


def test_returns_encounters_for_patient(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    encounters = get_encounters(backend, patient_id="p1")
    assert encounters
    assert all(e["resourceType"] == "Encounter" for e in encounters)
