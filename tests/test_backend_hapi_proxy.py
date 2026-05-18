from __future__ import annotations

from typing import Any

import httpx

from fhir_mcp.backend.hapi_proxy import HapiProxyBackend


def _mock_transport(responses: dict[str, Any]):
    """Returns an httpx transport that serves fixed JSON responses keyed by URL path."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        for key, data in responses.items():
            if path == key or path.endswith(key):
                return httpx.Response(200, json=data)
        return httpx.Response(404, json={"resourceType": "OperationOutcome"})

    return httpx.MockTransport(handler)


def test_read_patient_returns_resource() -> None:
    patient = {"resourceType": "Patient", "id": "p1"}
    transport = _mock_transport({"/Patient/p1": patient})

    backend = HapiProxyBackend("https://hapi.fhir.org/baseR4B", transport=transport)
    result = backend.read("Patient", "p1")

    assert result is not None
    assert result["id"] == "p1"
    assert result["resourceType"] == "Patient"


def test_read_missing_resource_returns_none() -> None:
    transport = _mock_transport({})

    backend = HapiProxyBackend("https://hapi.fhir.org/baseR4B", transport=transport)
    result = backend.read("Patient", "missing")

    assert result is None


def test_search_returns_bundle_entries() -> None:
    bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {"resource": {"resourceType": "Observation", "id": "obs1"}},
            {"resource": {"resourceType": "Observation", "id": "obs2"}},
        ],
    }
    transport = _mock_transport({"/Observation": bundle})

    backend = HapiProxyBackend("https://hapi.fhir.org/baseR4B", transport=transport)
    results = backend.search("Observation", {"patient": "p1"})

    assert len(results) == 2
    assert all(r["resourceType"] == "Observation" for r in results)


def test_search_empty_bundle_returns_empty_list() -> None:
    bundle = {"resourceType": "Bundle", "type": "searchset"}
    transport = _mock_transport({"/Observation": bundle})

    backend = HapiProxyBackend("https://hapi.fhir.org/baseR4B", transport=transport)
    results = backend.search("Observation", {})

    assert results == []
