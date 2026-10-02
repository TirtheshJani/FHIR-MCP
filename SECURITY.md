# Security Policy

## No real patient data

`fhir-mcp` is a research and demonstration project. It has **no authentication, authorization, encryption at rest, or audit logging**. It must **never** be used with real protected health information (PHI) or any other real patient data. Use only synthetic data such as the bundled Synthea bundle (`examples/synthea_patients.json.gz`).

If you expose the SSE transport on a network, treat everything it serves as public.

## Supported versions

Only the latest release on `main` receives fixes.

## Reporting a vulnerability

Please report security issues privately through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability") if it is enabled. Otherwise, open an issue that describes the affected area without exploit details and ask for a private channel. Never include real patient data in a report.
