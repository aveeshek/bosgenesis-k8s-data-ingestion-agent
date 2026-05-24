# Configuration Module Specification

## Implemented status

Runtime configuration is implemented in `src/bosgenesis_k8s_data_ingestion_agent/config`.

## Current configuration source

- Built-in defaults.
- Environment variables.

## Implemented settings groups

- Agent runtime and scheduler.
- REST API.
- Kubernetes Inspector MCP.
- Helm Manager MCP.
- PostgreSQL.
- ClickHouse.
- Qdrant.
- Redis.
- stdout sink.
- structured logging and service name.

## Secret handling

Secrets are loaded from environment variables and redacted from effective config output.

## Not implemented yet

- YAML/TOML config file loading.
- Langfuse/SigNoz runtime exporters.
