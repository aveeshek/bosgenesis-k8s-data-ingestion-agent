# Package Specification

## Role

This package will implement the runtime service for `bosgenesis-k8s-data-ingestion-agent`.

## Major module groups

- `entrypoints`
- `api`
- `scheduler`
- `core`
- `config`
- `mcp_clients`
- `collectors`
- `normalizers`
- `hashing`
- `change_detection`
- `sinks`
- `memory`
- `observability`
- `models`
- `security`
- `errors`

## Cross-cutting requirements

- Every scan has a run context.
- Every MCP call is allowlisted.
- Every sink failure follows configurable strict or non-strict behavior.
- Every emitted observation has a stable entity key and content hash.

