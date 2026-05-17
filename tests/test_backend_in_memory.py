from __future__ import annotations

from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend


def test_read_patient_by_id(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)

    patient = backend.read("Patient", "p1")

    assert patient is not None
    assert patient["resourceType"] == "Patient"
    assert patient["id"] == "p1"


def test_search_patients_returns_all_three(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)

    results = backend.search("Patient", criteria={})

    assert {p["id"] for p in results} == {"p1", "p2", "p3"}


def test_search_observations_for_patient(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)

    results = backend.search("Observation", criteria={"patient": "p1"})

    assert len(results) >= 1
    assert all(obs.get("subject", {}).get("reference", "").endswith("p1") for obs in results)
