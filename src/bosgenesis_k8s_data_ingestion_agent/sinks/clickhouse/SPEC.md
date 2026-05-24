# ClickHouse Sink Specification

## Role

The ClickHouse sink will store lightweight analytical facts and time-series events.

## Responsibilities

- Write run summary facts.
- Write resource status facts.
- Write Helm release facts.
- Write change-event facts.
- Support dashboard-friendly query patterns.

## Failure policy

ClickHouse write failures should not fail the whole scan unless strict mode is enabled.

