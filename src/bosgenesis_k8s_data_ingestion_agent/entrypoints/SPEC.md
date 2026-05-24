# Entrypoints Module Specification

## Implemented status

Entrypoints now start the agent in three runtime modes:

- `api`: FastAPI only.
- `scheduler`: periodic scanner only.
- `service`: FastAPI and scheduler together.

## Implemented responsibilities

- Parse CLI runtime mode.
- Load settings from environment variables.
- Configure structured JSON logging.
- Build the scan orchestrator and enabled sinks.
- Start Uvicorn for API mode.
- Start the scheduler loop for scheduler mode.
- Start API and scheduler concurrently for service mode.

## Non-responsibilities

- Entrypoints do not contain scan business logic.
- Entrypoints do not call MCP tools directly.
- Entrypoints only construct sink adapters; sink writes remain inside the sink layer.
