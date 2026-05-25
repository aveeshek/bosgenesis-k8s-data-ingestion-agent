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
- Optional MCP upstream `Host` header overrides.
- PostgreSQL.
- ClickHouse.
- Qdrant.
- Redis.
- stdout sink.
- structured logging and service name.

## Secret handling

Secrets are loaded from environment variables and redacted from effective config output.

The default deployment enables PostgreSQL and ClickHouse sinks, so production deployments must provide:

- `POSTGRES_DSN`
- `CLICKHOUSE_PASSWORD` when the configured ClickHouse user requires a password

For Helm installs, provide these through `charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml`, copied from the committed example.

## Not implemented yet

- YAML/TOML config file loading.
- Langfuse/SigNoz runtime exporters.
