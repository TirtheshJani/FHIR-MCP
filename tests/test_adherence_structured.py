from __future__ import annotations

from typing import Any

from fhir_mcp.adherence.structured import compute_structured_adherence
from fhir_mcp.backend.in_memory import InMemoryBackend


def test_returns_adherence_ratio_for_known_med(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)

    result = compute_structured_adherence(backend, patient_id="p1", medication="metformin")

    assert result["source"] == "structured"
    assert result["medication"] == "metformin"
    assert 0.0 <= result["adherence_ratio"] <= 1.0
    assert result["expected_doses"] >= result["observed_doses"]
