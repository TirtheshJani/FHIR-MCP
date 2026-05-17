# fhir-mcp: A FHIR R4B MCP Server with Evidence-Based Adherence Routing

## The problem: healthcare is underrepresented in the MCP ecosystem

The Model Context Protocol has seen rapid adoption in software engineering, productivity, and data analysis tools. Healthcare lags behind. A developer who wants to give an LLM agent access to FHIR R4B patient data today has to wire up raw HTTP calls, parse FHIR bundles manually, and build their own tool layer from scratch.

`fhir-mcp` changes that. It is an MIT-licensed Python MCP server that exposes five core FHIR R4B resource types as agent tools — Patient, Observation, MedicationRequest, Condition, Encounter — plus a composite tool called `compute_adherence` that does something more interesting: it routes adherence questions to the right pipeline based on what the question is actually asking.

## The research finding that motivated the routing design

In May 2026, Jani et al. published a preprint (arXiv ID TBD) studying how LLM agents should answer two different classes of clinical question over EHR data.

The paper compared two strategies on a benchmark of real clinical questions:

- **Structured FHIR pipeline**: query structured resources (MedicationRequest, Observation, Patient) and compute a quantitative answer.
- **Narrative RAG pipeline**: retrieve free-text clinical notes and let the model synthesize an answer.

The headline finding: neither approach dominates across all question types. The structured pipeline achieves AUC 0.997 on questions classified as "structured-FHIR-wins" — things like "did this patient fill their metformin prescription in Q1?" or "how many refill gaps occurred in 2025?". The narrative pipeline achieves AUC 0.843 on "narrative-wins" questions — things like "describe this patient's overall adherence behaviour" or "summarize their medication history in plain language".

The difference in AUC is large enough to matter clinically. Routing a date-bounded refill question through RAG costs you 15-20 percentage points of accuracy. Routing a free-text summary question through a structured pipeline produces an answer with no clinical nuance.

## How compute_adherence operationalizes the finding

`compute_adherence` is the only tool in fhir-mcp with branching logic. It takes three arguments: `patient_id`, `medication`, and `question`. The question text is passed through a `Router` that classifies intent.

v0.1.0 ships a `HeuristicRouter` that detects structured intent from patterns like date ranges, month names, four-digit years, the word "refill", and constructions like "did X take Y". It detects narrative intent from words like "describe", "summarize", "overall", and "pattern". When neither or both patterns fire, the branch is `ambiguous` and both pipelines run.

The `Router` is a Python Protocol, which means a future release can swap in the trained classifier from the Jani et al. preprint — once its weights are public — without touching any other file. That is the architectural payoff: the routing rule is isolated at one seam, tested independently, and swappable.

The structured branch computes a dose-count ratio from MedicationRequest dispense quantities and returns a JSON payload with `adherence_ratio`, `expected_doses`, `observed_doses`, and the observation period. The narrative branch returns DocumentReference and Composition resources as-is. Summarization is the agent's job, not the server's — the MCP boundary is preserved.

## Install and quickstart

```bash
pip install fhir-mcp
```

Drop this block into your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "fhir-mcp": {
      "command": "python",
      "args": [
        "-m", "fhir_mcp",
        "--bundle", "/absolute/path/to/synthea_patients.json.gz"
      ]
    }
  }
}
```

Restart Claude Desktop. The six tools appear immediately. Ask "find diabetic patients over 60" to start.

A demo bundle with 100 Synthea-generated FHIR R4B patients ships with the package at `examples/synthea_patients.json.gz`. All data is synthetic; no real PHI is included.

## Live reference deployment

A live SSE endpoint runs on Oracle Always Free ARM (Ampere aarch64). See `docs/DEPLOY_ORACLE.md` for the full provisioning runbook. The endpoint URL will be published once the 24-hour deployment soak passes.

For self-hosting, the repository includes a `docker/Dockerfile` (python:3.11-slim, multi-arch via buildx) and a `docker/docker-compose.yml` with a Caddy sidecar for automatic TLS via Let's Encrypt.

## What is next

v0.1.0 ships the heuristic router. v0.2 will swap it for the trained classifier from the Jani et al. preprint once the weights are publicly available. The `Router` protocol means that swap will be a single-file change.

Two other areas are tracked for v0.2: a HAPI FHIR R4B proxy backend (so the same tools work against a live R4B server, not just local bundles) and coverage of additional resource types like DiagnosticReport and AllergyIntolerance.

The project is listed in the public MCP server registry. Source, issues, and contributions: [github.com/TirtheshJani/FHIR-MCP](https://github.com/TirtheshJani/FHIR-MCP).

---

*Preprint citation: Jani et al., to appear, May 2026 (arXiv ID TBD). All performance figures are from that paper. Do not use fhir-mcp with real PHI; it is designed for synthetic Synthea data only.*
