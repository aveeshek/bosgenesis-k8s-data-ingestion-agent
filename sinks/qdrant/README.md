# Qdrant Sink Initialization

## Purpose

Qdrant stores semantic memory records for future troubleshooting, retrieval, and MoP-generation workflows.

## Default connection

Inside the BOS Genesis namespace:

```text
http://qdrant.bosgenesis.svc.cluster.local:6333
```

Ingress alternative:

```text
http://qdrant.bosgenesis.local
```

## Files

- `collection_payload.json`: collection definition for operational memory.
- `init_collections.sh`: creates or updates the collection by calling Qdrant HTTP API.

## Suggested execution

```bash
QDRANT_URL=http://qdrant.bosgenesis.svc.cluster.local:6333 \
QDRANT_COLLECTION=bosgenesis_k8s_observations \
VECTOR_SIZE=1536 \
sh sinks/qdrant/init_collections.sh
```

```bash
QDRANT_URL=http://10.105.157.24:6333 QDRANT_COLLECTION=bosgenesis_k8s_observations VECTOR_SIZE=1536 sh sinks/qdrant/init_collections.sh
```

Set `QDRANT_API_KEY` only if the cluster requires it.

