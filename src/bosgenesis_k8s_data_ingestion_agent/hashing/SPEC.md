# Hashing Module Specification

## Implemented status

The hashing module computes stable SHA-256 content hashes.

## Implemented responsibilities

- Recursively remove volatile fields.
- Serialize payloads deterministically with sorted keys.
- Compute SHA-256 content hashes.
- Apply hashes to observations with `hash_observations`.

## Volatile fields excluded

- `observed_at`
- `collection_timestamp`
- `run_id`
- `correlation_id`
- `resourceVersion`
- `resource_version`
- `managedFields`
- `managed_fields`
- `lastTransitionTime`
- `last_transition_time`
