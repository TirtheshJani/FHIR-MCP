from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


def test_mini_bundle_has_three_patients(mini_bundle: dict[str, Any]) -> None:
    patient_ids = {
        entry["resource"]["id"]
        for entry in mini_bundle["entry"]
        if entry["resource"]["resourceType"] == "Patient"
    }
    assert patient_ids == {"p1", "p2", "p3"}


def test_validate_bundle_script_exits_zero_on_mini_fixture() -> None:
    fixture = Path(__file__).parent / "fixtures" / "mini_bundle.json"
    script = Path(__file__).parent.parent / "scripts" / "validate_bundle.py"

    result = subprocess.run(
        [sys.executable, str(script), str(fixture)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
