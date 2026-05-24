# ClickHouse Sink Specification

## Implemented status

`ClickHouseSink` writes dashboard-oriented analytical facts.

## Implemented writes

- `scan_run_facts`
- `resource_status_facts`
- `helm_release_facts`
- `change_event_facts`

## Configuration

- `CLICKHOUSE_ENABLED`
- `CLICKHOUSE_HOST`
- `CLICKHOUSE_PORT`
- `CLICKHOUSE_USER`
- `CLICKHOUSE_PASSWORD`
- `CLICKHOUSE_DATABASE`

## Failure policy

Failures are handled by `SinkRouter`; strict mode raises, non-strict mode records failed sink result.
