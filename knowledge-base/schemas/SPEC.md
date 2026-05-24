# Schema Knowledge Specification

## Implemented status

Datastore schema initialization assets exist under the root `sinks` folder.

## Implemented schema assets

- PostgreSQL: `sinks/postgresql/init_schema.sql`
- pgvector optional table: `sinks/postgresql/init_pgvector.sql`
- ClickHouse: `sinks/clickhouse/init_schema.sql`
- Qdrant collection payload: `sinks/qdrant/collection_payload.json`
- Redis keyspace: `sinks/redis/keyspace.md`

## Runtime schema usage

Sink adapters write to the PostgreSQL, ClickHouse, Qdrant, and Redis shapes defined by those assets.
