# Operations Analysis Skill Specification

## Implemented status

No operations-analysis skill runtime is implemented yet.

## Available data sources

- PostgreSQL canonical snapshots.
- ClickHouse analytical facts.
- Qdrant semantic memory.
- Redis latest hash/cache and change stream.

## Responsibilities for future skill

- Retrieve observations.
- Summarize state and changes.
- Reference run IDs and entity hashes.
- Avoid triggering Kubernetes or Helm mutation.
