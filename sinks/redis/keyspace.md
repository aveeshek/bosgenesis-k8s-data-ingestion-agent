# Redis Keyspace Specification

## Prefix

All Redis keys use this prefix:

```text
bg:k8s-ingestion
```

Override with `REDIS_KEY_PREFIX` when needed.

## Keys

| Key pattern | Type | Purpose |
|---|---|---|
| `bg:k8s-ingestion:meta` | hash | Sink initialization metadata. |
| `bg:k8s-ingestion:latest-hash:{namespace}:{source}:{entity_key}` | string | Latest content hash for change detection. |
| `bg:k8s-ingestion:latest-run` | string or hash | Latest scan run summary pointer or compact summary. |
| `bg:k8s-ingestion:run:{run_id}:summary` | hash | Short-lived run summary. |
| `bg:k8s-ingestion:stream:changes` | stream | Change-event stream. |
| `bg:k8s-ingestion:stream:sink-audit` | stream | Sink write audit stream. |

## TTL guidance

- Latest hashes may be persistent or long-lived.
- Per-run summaries should use a TTL, for example 7 to 30 days.
- Streams should be trimmed by length or age by the runtime writer.

