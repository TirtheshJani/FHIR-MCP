from __future__ import annotations

from collections import defaultdict
from typing import Any


class InMemoryBackend:
    def __init__(self) -> None:
        self._by_id: dict[tuple[str, str], dict[str, Any]] = {}
        self._by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)

    @classmethod
    def from_bundle(cls, bundle: dict[str, Any]) -> InMemoryBackend:
        backend = cls()
        for entry in bundle.get("entry", []):
            resource = entry.get("resource") or entry
            rtype = resource.get("resourceType")
            rid = resource.get("id")
            if rtype and rid:
                backend._by_id[(rtype, rid)] = resource
                backend._by_type[rtype].append(resource)
        return backend

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        return self._by_id.get((resource_type, resource_id))

    def search(
        self,
        resource_type: str,
        criteria: dict[str, str],
    ) -> list[dict[str, Any]]:
        results = self._by_type.get(resource_type, [])
        patient_filter = criteria.get("patient")
        if patient_filter:
            results = [
                r
                for r in results
                if r.get("subject", {}).get("reference", "").endswith(patient_filter)
                or r.get("patient", {}).get("reference", "").endswith(patient_filter)
            ]
        return results
