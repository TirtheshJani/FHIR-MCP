# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

The repository is in a pre-scaffolding state — only `LICENSE` (MIT) and a stub `README.md` exist. There is no Python package, no tests, no build config yet. Treat the first task in any new session as "is the scaffold here?" — if not, create it before adding features.

### First scaffolding session — ordering

When the scaffold lands, build in this order. The `fhir_client.py` seam is the architectural lynchpin; validate it with one resource before committing five tools to it.

1. `pyproject.toml` (`[project].name = "fhir-mcp"`) + minimal `fhir_mcp/__init__.py` + `fhir_mcp/__main__.py`.
2. `fhir_client.py` with a `FhirClient` protocol and a `LocalBundleClient` impl reading a Synthea bundle from `data/synthea/`.
3. One resource tool end-to-end (Patient) wired into a running MCP server, tested against a local Synthea bundle, **before** adding Observation, MedicationRequest, Condition, Encounter.
4. Defer `compute_adherence` and `routing/` until the classifier artifact exists (see below).

## What this project is

`fhir-mcp` is a Python **Model Context Protocol (MCP)** server that exposes **FHIR R4B** resources as tools an LLM agent can call. The five primary resource tools are **Patient, Observation, MedicationRequest, Condition, Encounter**.

Resources must conform to **FHIR R4B specifically** — not R4 or R5. The shapes differ; Synthea must be invoked with an R4B-compatible profile (or a pre-generated R4B bundle source used) when producing test data.

The differentiator — and the reason this project exists — is one composite tool:

- **`compute_adherence`** routes incoming questions between two pipelines based on a published classifier from a May 2026 preprint (Jani et al. — fill citation in when public):
  - **structured-FHIR-wins-classification (AUC 0.997)** → route adherence-related questions to the **structured FHIR pipeline** (resource queries over Patient / MedicationRequest / Observation).
  - **narrative-wins-QA (AUC 0.843)** → route free-form clinical questions to a **RAG pipeline** over narrative notes.
  - The classifier **is not yet built**; weights/code location is **TBD**. Do not invent a substitute classifier — wait for the artifact or ask the user.

The MCP surface is intentionally small. The value is that `compute_adherence` operationalizes the preprint's routing finding inside an MCP tool an agent can call directly.

## Architecture

The package will be laid out in three layers:

- `fhir_mcp/server.py` — MCP server entrypoint; registers tools with Anthropic's Python MCP SDK.
- `fhir_mcp/fhir_client.py` — the **single seam** between tools and the underlying FHIR data source (local Synthea bundles or a live R4B server).
- `fhir_mcp/tools/` — one module per FHIR resource, plus `compute_adherence`.
- `fhir_mcp/routing/` — classifier + structured/RAG pipelines; only `compute_adherence` imports from here.

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

No build config exists yet. The first scaffolding session should set up `pyproject.toml` (hatchling or uv), `ruff` for lint+format, and `pytest`. Until then there are no working dev commands — do not document any here.

## Project skills (in `.claude/skills/`)

This project ships with five skills that constrain how sessions plan and build:

- `writing-plans` — required format for implementation plans (header, checkbox tasks, TDD steps, no placeholders). Plans live at `docs/superpowers/plans/YYYY-MM-DD-<name>.md`.
- `executing-plans` — load + execute an approved plan task by task.
- `test-driven-development` — mandatory for all production code. Red-green-refactor with watch-the-test-fail; see `testing-anti-patterns.md` for what to avoid.
- `dispatching-parallel-agents` — use when 2+ independent tasks have no shared state (e.g. the four resource tools in Phase 3 of the current plan).
- `karpathy-guidelines` — surface tradeoffs, simplicity first, surgical changes, goal-driven execution.

The current implementation plan is `docs/superpowers/plans/2026-05-17-fhir-mcp-v0.1.0.md`. Resolve its pre-flight open questions before starting Phase 1.

## Branch policy for this environment

Develop on `claude/fhir-mcp-server-tNLYt`. Push to that branch only.
