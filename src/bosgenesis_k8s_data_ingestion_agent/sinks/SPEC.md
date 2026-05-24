# Sinks Module Specification

## Implemented status

The sink layer contains the common interface, sink router, serialization helpers, and concrete sink adapters.

## Implemented responsibilities

- `BaseSink` protocol.
- `SinkRouter` writes to enabled sinks.
- Strict and non-strict sink error policy.
- Per-sink `SinkResult` with attempted/written counts and latency.
- Serialization helpers for JSON-safe sink payloads.
- Memory-capable sinks can also implement `write_memory(run_context, memory_records)`.

## Implemented sinks

- `PostgresSink`: scan runs, resource snapshots, Helm snapshots, change events, latest hash upserts.
- `ClickHouseSink`: analytical run, resource, Helm, and change-event facts.
- `QdrantSink`: semantic memory point upserts with pluggable embedding function and `write_memory`.
- `RedisSink`: latest hash keys, change stream, latest run pointer, run summary cache.
- `StdoutSink`: fallback/local output.
- `PgvectorSink`: placeholder still disabled behind `DisabledSink`.

## Not implemented yet

- LangMem sink.
- Letta sink runtime adapter.
