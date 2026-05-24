# Qdrant Sink Specification

## Implemented status

`QdrantSink` stores semantic operational memory points from either changed observations or prebuilt memory records.

## Implemented responsibilities

- Build legacy memory text from each changed record through `write()`.
- Accept session, episodic, and semantic `MemoryRecord` objects through `write_memory()`.
- Create deterministic point IDs from entity key and content hash.
- Attach run, correlation, namespace, source, entity, memory type, hash, status, and metadata payload.
- Use pluggable embedding function.
- Default to zero vectors when no embedding provider is configured.

## Configuration

- `QDRANT_ENABLED`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_COLLECTION`
- `QDRANT_VECTOR_SIZE`
