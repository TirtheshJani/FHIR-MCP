from __future__ import annotations

from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.tools.conditions import get_conditions


def test_returns_conditions_for_patient(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    conditions = get_conditions(backend, patient_id="p1")
    assert conditions
    assert all(c["resourceType"] == "Condition" for c in conditions)
