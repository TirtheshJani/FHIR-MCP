# Contributing to fhir-mcp

Thanks for your interest. Issues and pull requests are welcome.

## Setup

```bash
git clone https://github.com/TirtheshJani/FHIR-MCP.git
cd FHIR-MCP
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install        # optional: ruff + mypy on commit
```

## Before opening a PR

Run the same checks CI runs:

```bash
ruff check .
ruff format --check .
mypy
pytest -q
```

## Guidelines

- **Tests first.** Add a failing test, then the code that makes it pass.
- **Keep tools thin.** Resource tools are passthroughs over the `FhirBackend` protocol. Put logic in `compute_adherence` or a backend, not in individual tools.
- **FHIR R4B only.** Not R4 or R5.
- **Synthetic data only.** Use Synthea bundles. Never commit or test with real patient data (see `SECURITY.md`).
- **Small, focused PRs** from a feature branch to `main`, with a `CHANGELOG.md` entry under `[Unreleased]`.
- No em dashes in code, docs, or commit messages.
