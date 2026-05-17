from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from fhir.resources.bundle import Bundle


def validate(path: Path) -> int:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        raw = json.load(f)

    bundle = Bundle.model_validate(raw)
    print(f"bundle ok: {len(bundle.entry or [])} entries")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: validate_bundle.py <bundle.json|bundle.json.gz>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(validate(Path(sys.argv[1])))
