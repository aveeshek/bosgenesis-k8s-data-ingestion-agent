# Package Specification

## Implemented status

This package implements the runtime service foundation for `bosgenesis-k8s-data-ingestion-agent`.

## Module groups

- `entrypoints`: CLI and runtime mode selection.
- `api`: FastAPI routes for health, scan run, latest scan, and effective config.
- `scheduler`: periodic scan loop.
- `core`: scan orchestration.
- `config`: environment-based settings.
- `mcp_clients`: allowlisted MCP clients and in-memory test transport.
- `collectors`: Kubernetes and Helm raw bundle collection.
- `normalizers`: canonical observation conversion.
- `hashing`: stable content hash computation.
- `change_detection`: hash-state based change detection.
- `sinks`: sink router plus PostgreSQL, ClickHouse, Qdrant, Redis, pgvector placeholder, stdout.
- `memory`: thin session, episodic, and semantic memory abstraction.
- `observability`: detailed JSON logging.
- `models`: dataclass domain contracts.
- `security`: namespace validation and redaction helpers.
- `errors`: domain-specific exceptions.

## Cross-cutting requirements

- Every scan creates a `RunContext`.
- Every MCP call is checked against read allowlists and mutation denylists.
- Sink failures obey router strict/non-strict mode.
- Memory records can be routed to memory-capable sinks.
- Observations expose stable entity keys and content hashes.
- Secrets are redacted from normalized payloads and effective config output.
