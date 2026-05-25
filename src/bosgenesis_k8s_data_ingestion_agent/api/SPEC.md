# API Module Specification

## Implemented status

The API module exposes a FastAPI application through `create_app(settings, orchestrator)`.

## Implemented endpoints

- `GET /health`
- `POST /scan/run`
- `GET /scan/latest`
- `GET /config/effective`
- `POST /mcp`

## Implemented MCP tools

- `data_ingestion_health`
- `data_ingestion_run_scan`
- `data_ingestion_latest_scan`
- `data_ingestion_effective_config`

## Responsibilities

- Convert request payloads into `ScanRequest`.
- Delegate scan execution to `ScanOrchestrator`.
- Store the latest in-memory scan summary for `GET /scan/latest`.
- Mount the Streamable HTTP MCP app at `/mcp`.
- Return safe effective config with sink secrets redacted.

## Constraints

- REST and MCP entrypoints delegate to the same orchestrator/service layer.
- API does not write sinks directly.
- API does not expose secret values.
