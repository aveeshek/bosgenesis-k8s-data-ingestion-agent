# Normalizers Module Specification

## Implemented status

Normalizers convert raw Kubernetes and Helm MCP bundles into canonical `Observation` records.

## Implemented responsibilities

- Route bundles by source through `normalize_all`.
- Normalize Kubernetes pods, deployments, statefulsets, services, ingresses, PVCs, and events.
- Normalize Helm releases.
- Redact secret-like fields from raw and normalized payloads.
- Extract entity name, UID, type, status summary, and namespace.
- Populate `hash_input` from normalized payloads.

## Canonical observation fields

- observation ID
- run ID
- source
- namespace
- entity type
- entity name
- entity UID when available
- observed timestamp
- status summary
- raw payload
- normalized payload
- hash input
- content hash
