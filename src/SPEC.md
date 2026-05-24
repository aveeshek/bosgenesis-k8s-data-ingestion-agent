# Source Tree Specification

## Implemented status

The `src` tree now contains the Python package for `bosgenesis-k8s-data-ingestion-agent`.

## Package boundary

All runtime code lives under `src/bosgenesis_k8s_data_ingestion_agent`.

## Implemented modules

- Runtime entrypoints and mode selection.
- FastAPI application factory.
- Scheduler loop.
- Scan orchestration.
- Environment-driven configuration.
- MCP policy and client wrappers.
- Kubernetes and Helm collectors.
- K8s and Helm normalizers.
- Stable hashing and change detection.
- Sink router and concrete sink adapters.
- Structured JSON logging.
- Shared models, security helpers, and domain errors.

## Design principles

- Modules remain small and independently testable.
- External integrations are behind adapters.
- MCP read allowlists and mutation denylists are enforced in code.
- Unit and in-process e2e tests use fake transports and fake sink clients.
