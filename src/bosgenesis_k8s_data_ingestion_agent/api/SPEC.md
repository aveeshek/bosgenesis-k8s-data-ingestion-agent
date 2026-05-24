# API Module Specification

## Role

The API module will expose HTTP endpoints for health, scan triggering, latest summary, and effective non-secret configuration.

## Planned endpoints

- `GET /health`
- `POST /scan/run`
- `GET /scan/latest`
- `GET /config/effective`

## Responsibilities

- Validate request payloads.
- Create invocation metadata for manual or agent-triggered scans.
- Delegate scan execution to the orchestrator.
- Return run summaries and optional streamed output.

## Constraints

- Do not expose secrets.
- Do not bypass orchestrator lifecycle.
- Do not trigger Kubernetes or Helm mutation.

