# MCP Registry Entry: fhir-mcp

This document is the draft `server.json` submission for the official
Model Context Protocol server registry at
`github.com/modelcontextprotocol/registry`, plus the steps to file the PR.

The PR is filed manually, not by the agent. Treat this file as the
canonical source for the entry's content until it is merged upstream.

## server.json

The block below conforms to the `2025-12-11` `server.schema.json` published by
the registry. The `name` uses reverse-DNS namespacing tied to the GitHub
owner (`io.github.tirtheshjani/fhir-mcp`). The PyPI package is `fhir-mcp`
and the install command after publish will be `pip install fhir-mcp` (or
`uvx fhir-mcp` once a console script lands on PyPI).

```json
{
  "$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
  "name": "io.github.tirtheshjani/fhir-mcp",
  "title": "FHIR MCP",
  "description": "Model Context Protocol server for FHIR R4B. Exposes Patient, Observation, MedicationRequest, Condition, and Encounter as agent tools, plus a composite compute_adherence tool that routes between a structured FHIR pipeline and a narrative-resource pipeline.",
  "version": "0.1.0",
  "websiteUrl": "https://github.com/TirtheshJani/FHIR-MCP#readme",
  "repository": {
    "url": "https://github.com/TirtheshJani/FHIR-MCP",
    "source": "github"
  },
  "packages": [
    {
      "registryType": "pypi",
      "registryBaseUrl": "https://pypi.org",
      "identifier": "fhir-mcp",
      "version": "0.1.0",
      "runtimeHint": "uvx",
      "transport": {
        "type": "stdio"
      },
      "packageArguments": [
        {
          "type": "named",
          "name": "--bundle",
          "description": "Absolute path to a local Synthea FHIR R4B bundle file (.json or .json.gz) used as the in-memory backend.",
          "valueHint": "bundle_path",
          "isRequired": false
        }
      ],
      "environmentVariables": [
        {
          "name": "FHIR_MCP_BACKEND",
          "description": "Backend selector. Set to 'in_memory' (default) to read from --bundle, or 'hapi_proxy' to forward calls to a remote FHIR R4B HTTP server.",
          "default": "in_memory",
          "choices": ["in_memory", "hapi_proxy"],
          "isRequired": false
        },
        {
          "name": "FHIR_MCP_PROXY_URL",
          "description": "Base URL of the upstream FHIR R4B server. Required only when FHIR_MCP_BACKEND is 'hapi_proxy'.",
          "isRequired": false
        }
      ]
    }
  ],
  "remotes": [
    {
      "type": "sse",
      "url": "https://<your-hostname>/sse"
    }
  ]
}
```

TODO before submission: replace `https://<your-hostname>/sse` with the
public Oracle Always Free ARM endpoint once the deployment described in
`docs/DEPLOY_ORACLE.md` is live. If the endpoint is not live by submission
time, remove the `remotes` array entirely and ship a stdio-only entry; the
SSE entry can be added in a follow-up PR after the host is up.

Notes on the fields:

- `name` must contain exactly one `/` separating namespace from server name.
  `io.github.tirtheshjani` is the canonical reverse-DNS form for the GitHub
  account that owns the repo.
- `version` must track `pyproject.toml` `[project].version`. Bump both
  together when cutting a release.
- The PyPI package must be published before this entry will validate;
  publish `fhir-mcp==0.1.0` to PyPI first, then submit the registry PR.
- `runtimeHint: "uvx"` tells MCP clients they can run the server with
  `uvx fhir-mcp ...` without a manual `pip install`.
- `--bundle` is declared as a named argument with `isRequired: false`
  because the `hapi_proxy` backend does not need it.

## Submission steps

1. Publish `fhir-mcp==0.1.0` to PyPI from this repo, so the registry can
   resolve the `pypi` identifier during validation.
2. Fork `https://github.com/modelcontextprotocol/registry` to your GitHub
   account.
3. Clone your fork and create a branch, for example
   `add-fhir-mcp`.
4. Place the `server.json` content above at the path the registry's
   publisher tooling requires. As of the spec date below, the registry
   accepts entries via the `publisher` CLI (`make publisher` in the
   registry repo) which validates against
   `server.schema.json` and submits the entry. Run the validator locally
   before opening the PR: `tools/validate-*.sh server.json`.
5. Commit with message `Add fhir-mcp` and push the branch to your fork.
6. Open a pull request against `modelcontextprotocol/registry:main` with
   title `Add fhir-mcp`. In the PR body include:
   - link to this repo: `https://github.com/TirtheshJani/FHIR-MCP`
   - link to the quickstart in the README (the `Quick start with Claude
     Desktop` section)
   - link to a short screencast demonstrating the five resource tools and
     `compute_adherence` running against a Synthea bundle
   - link to the PyPI release page for `fhir-mcp==0.1.0`
7. Respond to reviewer comments. Update the `server.json` here in
   `docs/MCP_REGISTRY_ENTRY.md` to mirror any changes requested upstream,
   so this file stays the canonical draft.

Do not skip step 1. Submitting before the PyPI release exists will fail
schema validation on `packages[].identifier`.

## Spec reference

Sources consulted on 2026-05-18:

- `https://raw.githubusercontent.com/modelcontextprotocol/registry/main/README.md`
- `https://raw.githubusercontent.com/modelcontextprotocol/registry/main/docs/reference/server-json/generic-server-json.md`
- `https://raw.githubusercontent.com/modelcontextprotocol/registry/main/docs/reference/api/openapi.yaml`

If you are editing this file in the future, re-fetch the first two URLs.
The schema version embedded in `$schema` above
(`2025-12-11/server.schema.json`) is the version those docs pointed at on
the date above; check that the registry has not bumped to a newer
schema before submitting.
