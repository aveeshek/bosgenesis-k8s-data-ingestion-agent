# Memory Module Specification

## Role

The memory module will define extraction and routing rules for operational observations that should become future agent memory.

## Responsibilities

- Select high-signal records for memory.
- Avoid noisy repeated facts.
- Generate metadata for retrieval.
- Route memory candidates to Qdrant, pgvector, or LangMem-compatible adapters.

## Constraints

- Memory writing is optional.
- Letta adapter remains disabled by default.

