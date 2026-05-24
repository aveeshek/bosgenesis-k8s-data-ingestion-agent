# PostgreSQL Sink Specification

## Implemented status

`PostgresSink` writes durable canonical scan data to the `k8s_ingestion` schema.

## Implemented writes

- `scan_runs`
- `resource_snapshots`
- `helm_release_snapshots`
- `change_events`
- `latest_entity_hashes`

## Configuration

- `POSTGRES_ENABLED`
- `POSTGRES_DSN`

## Constraints

- The orchestrator passes only changed records to sinks.
- Payload redaction happens before observations reach sinks.
- Latest-hash lookup is not yet backed by PostgreSQL; current change detector uses a pluggable hash state store.
