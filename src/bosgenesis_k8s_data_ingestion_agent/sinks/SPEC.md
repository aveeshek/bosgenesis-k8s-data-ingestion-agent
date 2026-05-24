# Sinks Module Specification

## Role

Sinks will persist or emit scan observations and run summaries.

## Responsibilities

- Define common sink interface.
- Route writes to enabled sinks.
- Track per-sink success, latency, and failures.
- Support strict and non-strict error policy.
- Fall back to stdout or streaming output when no persistence sink is enabled.

## Sink families

- PostgreSQL.
- ClickHouse.
- Qdrant.
- pgvector.
- Redis.
- LangMem.
- Letta disabled adapter.
- Stdout or streaming.

