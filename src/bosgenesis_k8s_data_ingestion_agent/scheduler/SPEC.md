# Scheduler Module Specification

## Implemented status

The scheduler module implements an async loop that triggers scans at a configured interval.

## Implemented responsibilities

- Configurable `scan_interval_seconds`.
- Configurable namespace.
- Optional startup scan through `run_on_startup`.
- Stop hook for tests and controlled shutdown logic.
- Structured log events for scheduler ticks and startup scan.

## Constraints

- Scheduler only creates scheduled/startup `ScanRequest` objects.
- Scheduler delegates all scan work to `ScanOrchestrator`.
- Scheduler does not collect, normalize, compare, or persist data directly.
