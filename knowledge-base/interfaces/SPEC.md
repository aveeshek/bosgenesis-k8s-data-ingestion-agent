# Interface Knowledge Specification

## Implemented status

Interfaces are implemented across API, MCP clients, sinks, and memory routing.

## Implemented interfaces

- REST endpoints: `/health`, `/scan/run`, `/scan/latest`, `/config/effective`.
- Remote MCP endpoint: `/mcp`.
- MCP tools: `data_ingestion_health`, `data_ingestion_run_scan`, `data_ingestion_latest_scan`, `data_ingestion_effective_config`.
- Kubernetes MCP read allowlist.
- Helm MCP read allowlist.
- Sink protocol: async `write(run_context, records, summary)`.
- Memory sink protocol: async `write_memory(run_context, memory_records)`.
- Runtime CLI modes: `api`, `scheduler`, `service`.

## Not implemented yet

- Streamable HTTP MCP tool surface for this agent.
