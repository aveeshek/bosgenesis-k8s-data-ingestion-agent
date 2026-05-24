# Entrypoints Module Specification

## Role

Entrypoints will start the agent in service mode, API-only mode, scheduler-only mode, or future MCP-tool mode.

## Responsibilities

- Load effective configuration.
- Initialize observability.
- Initialize sink registry.
- Start REST API when enabled.
- Start periodic scheduler when enabled.
- Optionally run one startup scan.

## Non-responsibilities

- Do not contain scan business logic.
- Do not call MCP tools directly.
- Do not write persistence records directly.

