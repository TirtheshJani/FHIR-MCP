from __future__ import annotations

from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.tools.medications import get_medications


def test_returns_medication_requests_for_patient(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    meds = get_medications(backend, patient_id="p1")
    assert meds
    assert all(m["resourceType"] == "MedicationRequest" for m in meds)
    assert all(m.get("subject", {}).get("reference", "").endswith("p1") for m in meds)
