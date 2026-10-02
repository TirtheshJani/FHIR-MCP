# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

v0.1.0 is implemented and tested: a Python MCP server (`src/fhir_mcp`) exposing FHIR R4B resources as agent tools, with stdio and SSE transports, Docker, CI, and bundled synthetic data. v0.2.0 is planned in `docs/superpowers/plans/2026-05-18-fhir-mcp-v0.2.0.md`. When docs and code disagree, trust the code.

## What this project is

`fhir-mcp` is a **Model Context Protocol (MCP)** server that exposes **FHIR R4B** resources as tools an LLM agent can call:

- `fhir_search_patients`, `fhir_get_observations`, `fhir_get_medications`, `fhir_get_conditions`, `fhir_get_encounters` (thin passthroughs).
- `compute_adherence`, the composite tool and the reason the project exists. It routes a question to a structured pipeline (dose-count ratio over `MedicationRequest`), a narrative pipeline (`DocumentReference` + `Composition` for the agent to summarize), or both.

Resources must conform to **FHIR R4B specifically**, not R4 or R5. Synthea output is converted with `scripts/convert_r4_to_r4b.py` and checked with `scripts/validate_bundle.py`.

### Routing and the classifier

Routing today is `HeuristicRouter` in `src/fhir_mcp/adherence/routing.py`: regex keyword rules, behind a `Router` protocol (`detect(question) -> Intent`). The split is motivated by a May 2026 preprint (Jani et al., citation forthcoming; reported AUC 0.997 structured-wins classification, AUC 0.843 narrative-wins QA). Those numbers describe the preprint's classifier, not the heuristic.

The trained classifier **is not in this repo** and its artifact location is TBD. Do not invent a substitute classifier, new metrics, or a citation. Wait for the artifact or ask the user. The v0.2.0 plan adds an opt-in `ClassifierRouter` via `FHIR_MCP_ROUTER=classifier`.

## Architecture

```
src/fhir_mcp/
  __main__.py      CLI: --bundle (required), --transport {stdio,sse}, --port, --version
  server.py        FhirMcpServer: registers TOOL_DEF/handle from each tool module; sse_app()
  backend/
    base.py        FhirBackend protocol (read, search): the single data seam
    in_memory.py   InMemoryBackend.from_bundle(dict); search filters only on "patient"
    hapi_proxy.py  HapiProxyBackend (httpx, `proxy` extra); library only, not wired to CLI
  tools/           one module per resource: TOOL_NAME, TOOL_DEF (mcp.types.Tool), handle()
  adherence/
    routing.py     Intent, Router protocol, HeuristicRouter
    structured.py  compute_structured_adherence
    narrative.py   collect_narrative_resources
    compute.py     compute_adherence tool (TOOL_DEF + handle)
```

Key points:

- **Tool boundary = MCP tool.** Each tool takes a small typed argument set and returns JSON-serialisable FHIR resources as `TextContent`. Keep signatures stable; they are the agent-facing contract.
- **Data source is pluggable.** Tools only call `FhirBackend`. Do not branch on backend type inside a tool.
- **Only `compute_adherence` has logic.** Router and pipelines must stay unit-testable without an MCP server.
- **MCP SDK:** Anthropic's Python `mcp` package, pinned `<2` because 2.x removed the `Server.list_tools` / `Server.call_tool` decorators used in `server.py`. A 2.x migration is a deliberate future task, not a drive-by.

## Commands

```bash
pip install -e ".[dev]"                 # add ",proxy" for HapiProxyBackend
ruff check .                            # lint (CI)
ruff format --check .                   # format check (CI); *.md excluded
mypy                                    # strict, over src/fhir_mcp (CI)
pytest -q                               # all tests (CI)
pytest tests/test_server_stdio.py -q    # stdio round trip through a real subprocess
pytest tests/test_server_sse.py -q      # SSE round trip through in-process uvicorn

fhir-mcp --bundle examples/synthea_patients.json.gz                       # stdio
fhir-mcp --transport sse --port 8000 --bundle examples/synthea_patients.json.gz
docker build -f docker/Dockerfile -t fhir-mcp .                           # SSE on :8000
```

CI (`.github/workflows/ci.yml`) runs ruff check, ruff format --check, mypy, and pytest on `ubuntu-latest` and `ubuntu-24.04-arm` for Python 3.11 and 3.12, plus an arm64 Docker build and `/sse` smoke test. `publish.yml` publishes to PyPI on `v*` tags. Note: the PyPI name `fhir-mcp` is currently held by an unrelated project, so resolve naming before tagging a release.

## Data

Test and demo data is Synthea-generated FHIR R4B (`examples/synthea_patients.json.gz`, 100 patients; `tests/fixtures/mini_bundle.json`, patients p1 to p3). Do not commit PHI; do not pull from real clinical sources.

## Distribution and hosting

- Package name in `pyproject.toml`: `fhir-mcp`; console script `fhir-mcp`.
- Reference deployment: Oracle Cloud Always Free (ARM Ampere), see `docs/DEPLOY_ORACLE.md`. Keep anything platform-specific arm64-compatible.
- Demo path: Claude Desktop via `examples/claude_desktop_config.json`. Keep that flow working end to end.
- MCP registry entry draft: `docs/MCP_REGISTRY_ENTRY.md`.

## Project skills (in `.claude/skills/`)

- `writing-plans`: required format for implementation plans. Plans live at `docs/superpowers/plans/YYYY-MM-DD-<name>.md`.
- `executing-plans`: execute an approved plan task by task.
- `test-driven-development`: mandatory for production code (red, green, refactor; watch the test fail).
- `dispatching-parallel-agents`: for 2+ independent tasks with no shared state.
- `karpathy-guidelines`: surface tradeoffs, simplicity first, surgical changes, goal-driven execution.

## Repo conventions

- No em dashes in code, docs, or commit messages.
- Stage specific paths; never `git add -A`.
- Branches: develop on a feature branch (for example `claude/<topic>`) and open a PR to `main`. Never push to `main` without explicit permission.
