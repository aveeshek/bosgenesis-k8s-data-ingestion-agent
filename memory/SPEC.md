# Memory Folder Specification

## Implemented status

A thin agentic memory abstraction is implemented in the runtime package.

## Implemented memory behavior

- `MemoryRecordBuilder` creates session, episodic, and semantic records.
- `MemoryRouter` routes memory records to memory-capable sinks.
- `QdrantSink.write_memory()` persists memory records as semantic points.
- Embedding is pluggable; zero vectors are used when no embedder is configured.

## Future work

- pgvector runtime sink.
- LangMem adapter.
- Letta adapter.
