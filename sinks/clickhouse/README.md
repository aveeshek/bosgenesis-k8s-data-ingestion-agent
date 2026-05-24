# ClickHouse Sink Initialization

## Purpose

ClickHouse stores analytical facts and event-style rows for dashboards, trend analysis, and fast operational queries.

## Default connection

Inside the BOS Genesis namespace:

```text
host=clickhouse.bosgenesis.svc.cluster.local
http_port=8123
native_port=9000
user=bosgenesis
database=bosgenesis_k8s_ingestion
```

## Files

- `init_schema.sql`: creates the analytical database and MergeTree tables.

## Suggested execution

```bash
clickhouse-client --host clickhouse.bosgenesis.svc.cluster.local --port 9000 \
  --user bosgenesis --multiquery < sinks/clickhouse/init_schema.sql
```

```bash
clickhouse-client --host 10.105.114.74 --port 9000  --user bosgenesis --password <password> --multiquery < sinks/clickhouse/init_schema.sql
```

Or through HTTP:

```bash
curl -u "$CLICKHOUSE_USER:$CLICKHOUSE_PASSWORD" \
  --data-binary @sinks/clickhouse/init_schema.sql \
  http://clickhouse.bosgenesis.svc.cluster.local:8123/
```

