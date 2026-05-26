# Observability Module Specification

## Implemented status

Observability currently provides detailed structured JSON logging and optional Langfuse tracing.

## Implemented responsibilities

- `JsonFormatter` emits timestamp, level, logger, message, module, function, line, process, thread, and extra fields.
- `configure_logging()` installs JSON logging for the root logger.
- Scan, MCP, scheduler, and sink lifecycle events include structured `event` metadata.
- `LangfuseTracer` wraps scan runs in a root `data-ingestion.scan` trace.
- Child spans cover Kubernetes collection, Helm collection, normalization, hashing, change detection, sink writes, and memory writes.
- Traced scans add `trace_ids.langfuse` to `ScanSummary`.
- Missing Langfuse credentials or package availability fails soft and does not block scans.

## Not implemented yet

- OpenTelemetry/SigNoz spans.
- Metrics exporters.
