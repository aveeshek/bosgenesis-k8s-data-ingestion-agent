# Design Knowledge Specification

## Implemented status

The implemented design now includes runtime modes, API, scheduler, orchestrator, collectors, normalizers, hashing, change detection, sink adapters, thin memory abstraction, deployment, and tests.

## Current module boundaries

- API invokes orchestrator.
- Scheduler invokes orchestrator.
- Orchestrator coordinates collectors, normalization, hashing, change detection, sinks, and optional memory routing.
- MCP clients enforce read-only policy.
- Sinks own persistence/output behavior.
- Memory builder creates session, episodic, and semantic records.
- Memory router sends records to memory-capable sinks such as Qdrant.
