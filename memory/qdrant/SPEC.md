# Qdrant Memory Specification

## Implemented status

Qdrant runtime writes are implemented through `QdrantSink`, including direct memory-record writes.

## Implemented details

- Default collection: `bosgenesis_k8s_observations`.
- Default vector size: `1536`.
- Default URL: `http://qdrant.bosgenesis.svc.cluster.local:6333`.
- Observation payload includes text, run ID, correlation ID, namespace, source, entity, change type, content hash, observed time, status, and normalized metadata.
- Memory payload includes memory type, text, run ID, correlation ID, namespace, source, entity, content hash, observed time, and metadata.

## Bootstrap asset

- `sinks/qdrant/collection_payload.json`
