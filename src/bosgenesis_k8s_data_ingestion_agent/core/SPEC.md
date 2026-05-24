# Core Module Specification

## Role

The core module will contain orchestration, run context, sink routing, and high-level scan lifecycle coordination.

## Responsibilities

- Create `run_id` and `correlation_id`.
- Coordinate Kubernetes and Helm collection.
- Invoke normalization and hashing.
- Invoke change detection.
- Route records to enabled sinks.
- Build final run summaries.
- Handle partial failure policy.

## Key contracts

- Orchestrator contract.
- Run context contract.
- Scan request contract.
- Scan summary contract.
- Sink router contract.

