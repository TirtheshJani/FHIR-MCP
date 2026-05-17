from __future__ import annotations

from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.tools.observations import get_observations


def test_returns_observations_for_patient(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    observations = get_observations(backend, patient_id="p1", code=None)
    assert len(observations) >= 1
    assert all(o["resourceType"] == "Observation" for o in observations)


def test_filters_by_code(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    observations = get_observations(backend, patient_id="p1", code="2339-0")
    assert observations
    for o in observations:
        assert any(c["code"] == "2339-0" for c in o["code"]["coding"])
