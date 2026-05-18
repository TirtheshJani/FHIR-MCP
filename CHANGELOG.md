# Changelog

All notable changes to `fhir-mcp` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-18

### Added

- MCP tool `fhir_search_patients` for searching Patient resources by criteria.
- MCP tool `fhir_get_observations` for retrieving a patient's Observation history, with optional code filter.
- MCP tool `fhir_get_medications` for retrieving a patient's MedicationRequest history.
- MCP tool `fhir_get_conditions` for retrieving a patient's Condition list.
- MCP tool `fhir_get_encounters` for retrieving a patient's Encounter history.
- Composite MCP tool `compute_adherence` with a `HeuristicRouter` that dispatches to a structured FHIR pipeline, a narrative-resource pipeline, or both for ambiguous intent.
- `FhirBackend` protocol as the single seam between tools and data sources.
- `InMemoryBackend` for loading a Synthea FHIR R4B bundle from disk.
- Optional `HapiProxyBackend` (extra: `proxy`) that proxies reads and searches to a live FHIR R4B HTTP server via `httpx`.
- SSE transport in `server.py` and `__main__.py` for remote MCP clients, runnable via `python -m fhir_mcp --transport sse --port <int>`.
- `--version` flag on the CLI entrypoint.
- Synthea-generated 100-patient FHIR R4B bundle fixture at `examples/synthea_patients.json.gz` for demo and integration tests.
- `examples/claude_desktop_config.json` sample for wiring the server into Claude Desktop.
- Oracle Always Free ARM deployment runbook at `docs/DEPLOY_ORACLE.md`.

### Infrastructure

- Python project scaffold with `pyproject.toml` (hatchling), `src/` layout, and `fhir-mcp` console script.
- Ruff lint and format, mypy strict, pytest with `pytest-asyncio`, and pre-commit hooks.
- GitHub Actions CI workflow running ruff, mypy, and pytest on `ubuntu-latest` and `ubuntu-24.04-arm` across Python 3.11 and 3.12, plus a `linux/arm64` Docker build and SSE smoke test job.
- `docker/Dockerfile` buildable via `docker buildx` for both `linux/amd64` and `linux/arm64`, suitable for ARM Ampere hosts.
- `docker/docker-compose.yml` plus `docker/Caddyfile` for a Caddy TLS sidecar in front of the SSE endpoint, and `examples/demo_queries.md` listing example agent queries for the screencast.
- Synthea wrapper script and `validate_bundle.py` for regenerating and validating R4B test bundles.

[Unreleased]: https://github.com/TirtheshJani/FHIR-MCP/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/TirtheshJani/FHIR-MCP/releases/tag/v0.1.0
