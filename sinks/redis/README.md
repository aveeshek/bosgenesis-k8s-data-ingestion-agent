# Redis Sink Initialization

## Purpose

Redis stores latest entity hashes, short-lived run summaries, and stream-based write-audit events for fast change detection and operational inspection.

Redis does not have a schema in the relational sense. The initialization script creates key namespace metadata and optional streams/groups used by the agent.

## Default connection

Inside the BOS Genesis namespace:

```text
host=redis-master.bosgenesis.svc.cluster.local
port=6379
```

## Files

- `keyspace.md`: describes the Redis key layout.
- `init_keyspace.sh`: initializes metadata keys and consumer groups.

## Suggested execution

```bash
REDIS_HOST=redis-master.bosgenesis.svc.cluster.local \
REDIS_PORT=6379 \
sh sinks/redis/init_keyspace.sh
```

```bash
REDIS_HOST=10.98.119.245 REDIS_PORT=6379 sh sinks/redis/init_keyspace.sh
```

Set `REDIS_PASSWORD` only if the cluster requires it.

