from __future__ import annotations

import subprocess
import sys


def test_package_imports_with_version() -> None:
    import fhir_mcp

    assert isinstance(fhir_mcp.__version__, str)
    assert fhir_mcp.__version__ != ""


def test_version_flag_prints_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "fhir_mcp", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
