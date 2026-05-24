# Observability Module Specification

## Role

Observability will emit traces, spans, metrics, and structured logs for every scan.

## Responsibilities

- Create Langfuse trace per scan when enabled.
- Create OpenTelemetry spans for scan, collector, MCP call, normalization, change detection, and sink operations.
- Export OTLP traces to SigNoz when enabled.
- Produce structured JSON logs.
- Include run status, latency, counts, and error summaries.

