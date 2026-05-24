# Qdrant Sink Specification

## Role

The Qdrant sink will store semantic operational memory records when enabled.

## Responsibilities

- Build memory documents from useful observations.
- Attach metadata for namespace, entity type, entity name, run id, and hash.
- Avoid high-volume noisy data by default.
- Support future troubleshooting and MoP-generation retrieval.

