# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The repository is in a pre-scaffolding state — only `LICENSE` (MIT) and a stub `README.md` exist. There is no Python package, no tests, no build config yet. Treat the first task in any new session as "is the scaffold here?" — if not, create it before adding features.

## What this project is

`fhir-mcp` is a Python **Model Context Protocol (MCP)** server that exposes **FHIR R4B** resources as tools an LLM agent can call. The five primary resource tools are **Patient, Observation, MedicationRequest, Condition, Encounter**.

The differentiator — and the reason this project exists — is one composite tool:

- **`compute_adherence`** routes incoming questions between two pipelines based on a published classifier from a May 2026 preprint:
  - **structured-FHIR-wins-classification (AUC 0.997)** → route adherence-related questions to the **structured FHIR pipeline** (resource queries over Patient / MedicationRequest / Observation).
  - **narrative-wins-QA (AUC 0.843)** → route free-form clinical questions to a **RAG pipeline** over narrative notes.

The MCP surface is intentionally small. The value is that `compute_adherence` operationalizes the preprint's routing finding inside an MCP tool an agent can call directly.

## Planned architecture (build toward this)

```
fhir_mcp/
  server.py            # MCP server entrypoint; registers tools
  fhir_client.py       # Thin wrapper over a FHIR R4B endpoint (or local Synthea bundles)
  tools/
    patient.py
    observation.py
    medication_request.py
    condition.py
    encounter.py
    compute_adherence.py   # routing classifier + dispatch
  routing/
    classifier.py      # structured-vs-narrative router from the preprint
    structured.py      # adherence pipeline over FHIR resources
    rag.py             # narrative QA pipeline
data/
  synthea/             # Synthea-generated FHIR bundles (MIT-licensed test data)
tests/
```

Key architectural points that span files:

- **Tool boundary = MCP tool, not Python function.** Each FHIR resource tool should accept a small, typed argument set (e.g. `patient_id`, search params) and return JSON-serialisable FHIR resources. Tools are the agent-facing contract; keep their signatures stable.
- **Data source is pluggable.** The same tool implementations must work against (a) local Synthea bundles loaded from disk for tests/demo and (b) a live FHIR R4B server. Put that switch behind `fhir_client.py`; do not branch on it inside individual tools.
- **`compute_adherence` is the only tool with routing logic.** All other tools are thin FHIR passthroughs. The classifier lives in `routing/classifier.py` and must be unit-testable without an MCP server running.
- **MCP SDK is Anthropic's Python MCP SDK.** Follow the SDK's tool registration patterns; don't invent a parallel abstraction.

## Distribution & hosting plan

- **PyPI package name: `fhir-mcp`** — keep `pyproject.toml` `[project].name` consistent.
- **Reference deployment: Oracle Cloud Always Free (ARM Ampere).** Anything platform-specific (systemd unit, Docker for arm64) should be ARM-compatible.
- **Demo path: Claude Desktop.** README install instructions target Claude Desktop's MCP config; keep that flow working end-to-end.
- **Listed in the public MCP server registry** once shipped.

## Data

Test/demo data is **Synthea-generated FHIR R4B bundles** (MIT licensed, no credentialing needed). Do not commit PHI; do not pull from real clinical sources.

## Commands

Conventions to use once `pyproject.toml` exists (none of these work yet — set them up first):

- Install dev: `pip install -e ".[dev]"`
- Run the MCP server: `python -m fhir_mcp` (or the entry point declared in `pyproject.toml`)
- Tests: `pytest`
- Single test: `pytest tests/test_x.py::test_name`
- Lint/format: `ruff check .` and `ruff format .`

## Branch policy for this environment

Develop on `claude/fhir-mcp-server-tNLYt`. Push to that branch only.
