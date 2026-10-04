[![CI](https://github.com/TirtheshJani/FHIR-MCP/actions/workflows/ci.yml/badge.svg)](https://github.com/TirtheshJani/FHIR-MCP/actions/workflows/ci.yml)

# fhir-mcp

Model Context Protocol server for FHIR R4B. Exposes Patient, Observation,
MedicationRequest, Condition, Encounter as agent tools, plus a composite
`compute_adherence` tool that routes between a structured FHIR pipeline and a
narrative-resource pipeline.

## Install

```bash
pip install git+https://github.com/TirtheshJani/FHIR-MCP.git
```

## Quick start with Claude Desktop

Merge this block into `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

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

Restart Claude Desktop. Ask: "find diabetic patients over 60."

## Tools

| Tool | Returns |
|------|---------|
| `fhir_search_patients(criteria)` | List of Patient resources |
| `fhir_get_observations(patient_id, code?)` | Observation history, optionally filtered by code |
| `fhir_get_medications(patient_id)` | MedicationRequest history |
| `fhir_get_conditions(patient_id)` | Condition list |
| `fhir_get_encounters(patient_id)` | Encounter history |
| `compute_adherence(patient_id, medication, question)` | Routed adherence answer |

## `compute_adherence` routing rule

Heuristic intent router classifies the question as:

- **structured** (date ranges, medication names, "did X take Y", refill count)
  runs a dose-count ratio over MedicationRequest and Observation.
- **narrative** (describe, summarize, overall, pattern) returns
  DocumentReference and Composition resources for the agent to summarize.
- **ambiguous** runs both and returns both.

The routing rule is motivated by Jani (2026), "Representation Wins on
QA, Not on ML" (completed manuscript, May 2026; Zenodo deposit,
doi:10.5281/zenodo.20263384; arXiv submission pending). On 200
synthetic patients and 13,800 adherence questions, narrative RAG won
free-form QA (40.6% exact match, against 35.3% and 33.4% for the two
structured systems), and structured FHIR features won adherence
prediction (LightGBM AUC 0.997, against 0.846 for narrative features).
The Router protocol allows
a future v0.2 release to swap the heuristic for the trained classifier
with no other code changes.

## Data

Test bundles are Synthea v3+ generated, FHIR R4B, MIT-licensed.
Do NOT use this server with real PHI. See `examples/` for sample data.

## Reference deployment

`docs/DEPLOY_ORACLE.md` is the runbook for serving this over SSE on an
Oracle Always Free ARM instance. No public endpoint URL is published.

## License

MIT. See `LICENSE`.
