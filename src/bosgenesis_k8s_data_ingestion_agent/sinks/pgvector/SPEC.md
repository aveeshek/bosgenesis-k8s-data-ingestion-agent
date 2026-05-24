# pgvector Sink Specification

## Role

The pgvector sink will store vector memory records in PostgreSQL when enabled.

## Responsibilities

- Share connection configuration with PostgreSQL where appropriate.
- Store embedding vectors and metadata.
- Support future semantic retrieval workflows.

## Constraints

- Do not require pgvector when PostgreSQL snapshot storage is enabled.
- Keep vector writes optional.

