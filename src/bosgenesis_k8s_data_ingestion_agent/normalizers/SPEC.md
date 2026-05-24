# Normalizers Module Specification

## Role

Normalizers will transform raw MCP payloads into canonical observation records.

## Responsibilities

- Convert heterogeneous Kubernetes and Helm payloads into a common observation shape.
- Preserve raw payload references where configured.
- Create stable entity identifiers.
- Extract status summaries for analytics and memory.
- Prepare hash input payloads by excluding volatile fields.

## Canonical observation fields

- Observation identifier.
- Run identifier.
- Source.
- Namespace.
- Entity type.
- Entity name.
- Entity UID when available.
- Observed timestamp.
- Status summary.
- Raw payload.
- Normalized payload.
- Hash input.
- Content hash placeholder.

