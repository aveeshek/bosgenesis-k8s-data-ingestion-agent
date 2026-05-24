# API Module Specification

## Implemented status

The API module exposes a FastAPI application through `create_app(settings, orchestrator)`.

## Implemented endpoints

- `GET /health`
- `POST /scan/run`
- `GET /scan/latest`
- `GET /config/effective`

## Responsibilities

- Convert request payloads into `ScanRequest`.
- Delegate scan execution to `ScanOrchestrator`.
- Store the latest in-memory scan summary for `GET /scan/latest`.
- Return safe effective config with sink secrets redacted.

## Constraints

- API does not call MCP tools directly.
- API does not write sinks directly.
- API does not expose secret values.
