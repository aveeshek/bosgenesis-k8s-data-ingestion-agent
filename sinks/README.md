# Sink Initialization Assets

This folder contains datastore bootstrap assets for `bosgenesis-k8s-data-ingestion-agent`.

These files initialize schemas, tables, collections, streams, and cache key namespaces used by the future runtime sink adapters.

## BOS Genesis service defaults

The scripts assume the agent runs inside the `bosgenesis` namespace and can reach these Kubernetes services:

| Sink | Service | Port | Default user |
|---|---|---:|---|
| PostgreSQL | `postgresql.bosgenesis.svc.cluster.local` | `5432` | `bosgenesis` |
| ClickHouse | `clickhouse.bosgenesis.svc.cluster.local` | `8123` | `bosgenesis` |
| Qdrant | `qdrant.bosgenesis.svc.cluster.local` | `6333` | not required by default |
| Redis | `redis-master.bosgenesis.svc.cluster.local` | `6379` | not required by default |

Ingress alternatives from the observed cluster:

- `qdrant.bosgenesis.local`
- `ch-ui.bosgenesis.local`
- `clickhouse-mcp.bosgenesis.local`
- `redisinsight.bosgenesis.local`

## Folder map

- `postgresql/`: canonical relational schema for scan runs, snapshots, events, latest hashes, and optional vector memory.
- `clickhouse/`: analytical fact and event tables optimized for dashboard queries.
- `qdrant/`: semantic memory collection initialization.
- `redis/`: cache key namespace and stream/group initialization.

## Execution posture

- These scripts create storage primitives only.
- They do not collect Kubernetes or Helm data.
- They do not mutate Kubernetes or Helm resources.
- They do not embed passwords or secrets.

