# Change Detection Module Specification

## Role

Change detection will compare current observation hashes against latest known state.

## Responsibilities

- Determine changed, unchanged, new, and removed entities.
- Prefer Redis latest-state cache when enabled.
- Fall back to PostgreSQL latest hash lookup when enabled.
- Treat all observations as output records when no comparison store exists.
- Respect full-history mode when configured.

## Outputs

- Changed record set.
- Unchanged count.
- Entity lifecycle events.
- Change reason metadata when inferable.

