# Memory Module Specification

## Implemented status

The memory module now provides a thin agentic memory abstraction.

## Implemented components

- `MemoryType`
- `MemoryRecord`
- `MemoryRecordBuilder`
- `MemoryRouter`

## Current behavior

- Session memory records summarize scan runs.
- Episodic memory records summarize observed change events.
- Semantic memory records summarize compact operational facts.
- Memory routing targets sinks that implement `write_memory`.
- Qdrant supports `write_memory`.

## Not implemented yet

- LangMem adapter.
- Letta adapter.
- pgvector runtime writer.
