# Redis Sink Specification

## Implemented status

`RedisSink` writes latest hash cache records, change stream events, and run summary cache entries.

## Implemented writes

- `bg:k8s-ingestion:latest-hash:{namespace}:{source}:{entity_key}`
- `bg:k8s-ingestion:stream:changes`
- `bg:k8s-ingestion:latest-run`
- `bg:k8s-ingestion:run:{run_id}:summary`

## Configuration

- `REDIS_ENABLED`
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `REDIS_PASSWORD`
- `REDIS_KEY_PREFIX`

## Constraints

- Redis remains a cache/stream sink, not the long-term source of truth.
- Change detection does not yet read Redis directly.
