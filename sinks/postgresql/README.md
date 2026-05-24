# PostgreSQL Sink Initialization

## Purpose

PostgreSQL is the durable canonical store for scan runs, Kubernetes resource snapshots, Helm release snapshots, change events, and latest entity hashes.

## Default connection

Inside the BOS Genesis namespace:

```text
host=postgresql.bosgenesis.svc.cluster.local
port=5432
user=bosgenesis
database=bosgenesis
```

## Files

- `init_schema.sql`: creates the `k8s_ingestion` schema and core tables.
- `init_pgvector.sql`: optional vector-memory table. Run only when the `vector` extension is installed.

## Suggested execution

```bash
psql "$POSTGRES_DSN" -f sinks/postgresql/init_schema.sql
psql "$POSTGRES_DSN" -f sinks/postgresql/init_pgvector.sql
```

## Data model intent

- `scan_runs`: one row per scan execution.
- `resource_snapshots`: changed Kubernetes resource observations.
- `helm_release_snapshots`: changed Helm release observations.
- `change_events`: normalized change timeline.
- `latest_entity_hashes`: fast durable hash lookup for deduplication.
- `memory_vectors`: optional vector memory records for retrieval workflows.

