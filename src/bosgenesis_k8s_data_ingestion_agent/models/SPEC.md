# Models Module Specification

## Implemented status

Models are implemented as dataclasses and enums shared across the package.

## Implemented models

- `ScanStatus`
- `ChangeType`
- `ScanRequest`
- `RunContext`
- `RawBundle`
- `Observation`
- `ChangeRecord`
- `SinkResult`
- `ScanSummary`

## Constraints

- Models have no dependency on concrete external clients.
- `Observation` separates raw payload, normalized payload, hash input, and content hash.
- `Observation.entity_key` provides stable identity for sinks and change detection.
