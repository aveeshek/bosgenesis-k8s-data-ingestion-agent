# Runtime Config Module Specification

## Implemented status

The config module provides dataclass settings loaded from environment variables.

## Implemented settings

- `AgentSettings`
- `ApiSettings`
- `McpEndpointSettings`
- `SinkSettings`
- `ObservabilitySettings`
- `Settings`

## Implemented environment support

- Agent namespace, startup scan, scan interval, strict sink mode.
- API host and port.
- K8s and Helm MCP endpoint URLs, timeouts, and retries.
- PostgreSQL DSN.
- ClickHouse host, port, user, password, and database.
- Qdrant URL, API key, collection, and vector size.
- Redis host, port, DB, password, and key prefix.
- stdout sink enablement.
- log level and service name.

## Secret handling

`effective_safe_dict()` redacts:

- `postgres_dsn`
- `clickhouse_password`
- `qdrant_api_key`
- `redis_password`
