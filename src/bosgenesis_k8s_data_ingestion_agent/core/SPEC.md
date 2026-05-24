# Core Module Specification

## Implemented status

The core module contains `ScanOrchestrator`, which coordinates the full scan lifecycle.

## Implemented responsibilities

- Create `RunContext` with `run_id`, `correlation_id`, namespace, trigger type, and start time.
- Call Kubernetes and Helm collectors when configured.
- Normalize raw bundles into observations.
- Compute stable content hashes.
- Detect new, changed, and unchanged records.
- Route changed records to enabled sinks.
- Optionally build session, episodic, and semantic memory records.
- Optionally route memory records to memory-capable sinks.
- Build scan summaries.
- Convert unexpected exceptions into failed summaries.
- Emit structured scan lifecycle logs.

## Key contracts

- `RunContext`
- `ScanRequest`
- `RawBundle`
- `Observation`
- `ChangeRecord`
- `ScanSummary`
- `SinkRouter`
- `MemoryRecordBuilder`
- `MemoryRouter`
