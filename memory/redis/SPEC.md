# Redis Memory Specification

## Implemented status

Redis runtime writes are implemented through `RedisSink`.

## Implemented behavior

- latest hash keys
- change stream events
- latest run pointer
- TTL-based run summary cache

## Bootstrap assets

- `sinks/redis/keyspace.md`
- `sinks/redis/init_keyspace.sh`
- `sinks/redis/init_keyspace.py`
