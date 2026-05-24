# Stdout and Streaming Sink Specification

## Role

The stdout or streaming sink will emit scan results when persistence is disabled or when requested by the caller.

## Responsibilities

- Return or print normalized observations safely.
- Redact configured sensitive fields.
- Preserve run summary metadata.
- Support on-demand callers that need immediate data.

