# PostgreSQL Sink Specification

## Role

The PostgreSQL sink will store canonical run and snapshot records for future ML and audit analysis.

## Responsibilities

- Store scan runs.
- Store Kubernetes resource snapshots.
- Store Helm release snapshots.
- Store change events.
- Support latest-hash lookup for change detection.

## Constraints

- Store only changed snapshots unless full-history mode is enabled.
- Avoid storing secrets or unredacted secret-like values.

