# Stdout and Streaming Sink Specification

## Implemented status

`StdoutSink` stores JSON lines in-memory for tests and local fallback behavior.

## Implemented responsibilities

- Emit changed records as compact JSON lines.
- Include run ID, correlation ID, namespace, source, entity, change type, and content hash.
- Return `SinkResult`.

## Current limitation

- It does not currently print directly to process stdout; it keeps emitted lines on the sink instance.
