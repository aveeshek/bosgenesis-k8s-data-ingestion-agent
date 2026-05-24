# Configuration Module Specification

## Role

The `config` directory will define the future non-secret configuration layout for the agent.

## Responsibilities

- Specify default settings for agent runtime, API, scheduler, MCP clients, sinks, memory, and observability.
- Separate non-secret settings from secret references.
- Define configuration precedence: defaults, settings file, environment variables.
- Support enabling or disabling every external sink independently.

## Key settings groups

- Agent runtime settings.
- REST API settings.
- Scheduler settings.
- Kubernetes Inspector MCP settings.
- Helm Manager MCP settings.
- PostgreSQL and pgvector settings.
- ClickHouse settings.
- Qdrant settings.
- Redis settings.
- LangMem and Letta settings.
- Langfuse and SigNoz OpenTelemetry settings.

