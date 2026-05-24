# Change Detection Module Specification

## Implemented status

Change detection compares current observation hashes against a pluggable latest-hash store.

## Implemented responsibilities

- Detect `new`, `changed`, and `unchanged`.
- Update latest hash state for new and changed records.
- Support full-history mode.
- Provide `InMemoryHashStateStore` for tests and local runs.

## Current limitations

- Deleted or missing resource candidate detection is not implemented yet.
- Redis/PostgreSQL-backed hash state lookup can be added behind the `HashStateStore` protocol.

## Outputs

- `ChangeRecord` with observation, change type, and previous hash.
