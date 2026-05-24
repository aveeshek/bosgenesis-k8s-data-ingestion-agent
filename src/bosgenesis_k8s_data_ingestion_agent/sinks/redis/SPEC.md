# Redis Sink Specification

## Role

The Redis sink will cache latest resource hash state and short-lived run metadata.

## Responsibilities

- Store latest entity hash by namespace and entity key.
- Store latest run summary when enabled.
- Support TTL configuration for transient data.
- Accelerate change detection.

## Constraints

- Redis is an optimization, not the source of long-term analytical truth.

