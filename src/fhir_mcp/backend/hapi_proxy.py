from __future__ import annotations

from typing import Any

import httpx


class HapiProxyBackend:
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._client = httpx.Client(timeout=timeout, transport=transport)

    def read(self, resource_type: str, resource_id: str) -> dict[str, Any] | None:
        r = self._client.get(f"{self._base}/{resource_type}/{resource_id}")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()  # type: ignore[no-any-return]

    def search(self, resource_type: str, criteria: dict[str, str]) -> list[dict[str, Any]]:
        r = self._client.get(f"{self._base}/{resource_type}", params=criteria)
        r.raise_for_status()
        bundle: dict[str, Any] = r.json()
        return [e["resource"] for e in bundle.get("entry", [])]
