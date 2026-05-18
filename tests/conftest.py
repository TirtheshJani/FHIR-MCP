from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mini_bundle.json"


@pytest.fixture
def mini_bundle() -> dict[str, Any]:
    with FIXTURE_PATH.open() as f:
        return json.load(f)
