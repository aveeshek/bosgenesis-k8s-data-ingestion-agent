# Hashing Module Specification

## Role

The hashing module will compute stable content fingerprints for observations.

## Responsibilities

- Exclude volatile fields from hash input.
- Serialize normalized payloads deterministically.
- Compute SHA-256 or approved equivalent content hashes.
- Provide entity-key helpers for change detection.

## Volatile fields to exclude

- Collection timestamp.
- Observed timestamp.
- Run identifier.
- Correlation identifier.
- Noisy resource versions when configured.
- Managed fields when present.
- Highly volatile transition timestamps when configured.

