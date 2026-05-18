from __future__ import annotations

import json
from typing import Any

from fhir_mcp.backend.in_memory import InMemoryBackend
from fhir_mcp.tools.patients import TOOL_DEF, TOOL_NAME, handle


def test_tool_name_and_def() -> None:
    assert TOOL_NAME == "fhir_search_patients"
    assert TOOL_DEF.name == TOOL_NAME


def test_handle_returns_all_patients(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = handle(backend, {"criteria": {}})
    patients = json.loads(result[0].text)
    assert {p["id"] for p in patients} == {"p1", "p2", "p3"}


def test_handle_returns_text_content(mini_bundle: dict[str, Any]) -> None:
    backend = InMemoryBackend.from_bundle(mini_bundle)
    result = handle(backend, {"criteria": {}})
    assert result[0].type == "text"
    assert isinstance(result[0].text, str)
