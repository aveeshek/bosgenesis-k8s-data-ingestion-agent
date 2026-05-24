# Models Module Specification

## Role

Models will define typed contracts shared across modules.

## Model groups

- Scan request.
- Run context.
- Raw collection bundle.
- Canonical observation.
- Hashed observation.
- Change record.
- Sink result.
- Run summary.
- Error summary.

## Constraints

- Models should avoid dependency on concrete external clients.
- Models should separate raw payloads from normalized payloads.

