from __future__ import annotations

from typing import Any, Protocol


class FhirBackend(Protocol):
    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None: ...

    def search(
        self,
        resource_type: str,
        criteria: dict[str, str],
    ) -> list[dict[str, Any]]: ...
