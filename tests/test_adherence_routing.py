from __future__ import annotations

from typing import Any

import pytest

from fhir_mcp.adherence.compute import compute_adherence
from fhir_mcp.adherence.routing import HeuristicRouter, Intent
from fhir_mcp.backend.in_memory import InMemoryBackend


@pytest.mark.parametrize(
    "question,expected",
    [
        ("Did patient p1 take metformin between Jan and June 2026?", Intent.STRUCTURED),
        ("How many refills did patient p1 get for metformin?", Intent.STRUCTURED),
        ("Describe patient p1's overall adherence pattern.", Intent.NARRATIVE),
        ("Summarize this patient's medication history.", Intent.NARRATIVE),
        ("Tell me about patient p1.", Intent.AMBIGUOUS),
    ],
)
def test_detect_intent(question: str, expected: Intent) -> None:
    router = HeuristicRouter()
    assert router.detect(question) == expected


def test_structured_branch(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = compute_adherence(
        backend,
        patient_id="p1",
        medication="metformin",
        question="Did patient p1 take metformin between Jan and June 2026?",
    )
    assert result["branch"] == "structured"
    assert "adherence_ratio" in result["structured"]


def test_narrative_branch(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = compute_adherence(
        backend,
        patient_id="p1",
        medication="metformin",
        question="Describe patient p1's overall adherence pattern.",
    )
    assert result["branch"] == "narrative"
    assert result["narrative"]["resources"]


def test_ambiguous_branch_runs_both(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = compute_adherence(
        backend,
        patient_id="p1",
        medication="metformin",
        question="Tell me about patient p1.",
    )
    assert result["branch"] == "ambiguous"
    assert "structured" in result and "narrative" in result
