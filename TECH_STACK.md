# Frameworks, Libraries, Tools, and Components

## Runtime language and service framework

- Python 3.11 or newer
- FastAPI for REST API endpoints
- Uvicorn for ASGI serving
- Pydantic v2 and pydantic-settings for typed configuration and DTOs
- APScheduler or equivalent async scheduler for periodic scans
- httpx for remote MCP HTTP calls

## MCP and agent interfaces

- Model Context Protocol Python SDK for optional MCP tool surface
- Existing BOS Genesis Kubernetes Inspector MCP server
- Existing BOS Genesis Helm Manager MCP server
- Optional LangGraph or LangMem-compatible hooks for future memory workflows

## Persistence and analytics

- PostgreSQL for canonical scan runs, resource snapshots, Helm snapshots, and change events
- pgvector for vector memory inside PostgreSQL when enabled
- ClickHouse for analytical facts, events, and time-series dashboard data
- Qdrant for semantic memory indexing when enabled
- Redis for latest-state hash cache and short-lived run metadata

## Observability

- Langfuse for agent and operation traces
- OpenTelemetry SDK for spans and metrics
- OTLP exporter for SigNoz
- python-json-logger or structlog for structured logs

## Kubernetes and deployment

- Docker or equivalent OCI image build tool
- Kubernetes Deployment, Service, ConfigMap, Secret reference, ServiceAccount, Role, RoleBinding, NetworkPolicy, and optional Ingress
- Helm v3 chart for packaging and environment-specific values
- Namespace-scoped RBAC only

## Development quality gates

- pytest for unit and contract tests
- pytest-asyncio for async flows
- respx or pytest-httpx for MCP client stubbing
- Ruff for linting and formatting
- mypy or pyright for type checking
- pre-commit for local quality checks

## Security and configuration

- Environment variable based secret injection
- YAML or TOML non-secret settings file
- Kubernetes Secret references for credentials
- Explicit MCP allowlists and mutation denylists
- Bounded log collection configuration

