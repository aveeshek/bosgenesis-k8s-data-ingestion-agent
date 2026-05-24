# Observability Module Specification

## Implemented status

Observability currently provides detailed structured JSON logging.

## Implemented responsibilities

- `JsonFormatter` emits timestamp, level, logger, message, module, function, line, process, thread, and extra fields.
- `configure_logging()` installs JSON logging for the root logger.
- Scan, MCP, scheduler, and sink lifecycle events include structured `event` metadata.

## Not implemented yet

- Langfuse traces.
- OpenTelemetry/SigNoz spans.
- Metrics exporters.
