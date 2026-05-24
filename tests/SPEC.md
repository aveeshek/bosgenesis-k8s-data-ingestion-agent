# Tests Specification

## Implemented status

The test suite now includes unit tests, sink adapter tests with fakes, and in-process e2e tests.

## Implemented categories

- Config tests.
- Security/redaction tests.
- Structured logging tests.
- MCP policy and client tests.
- Collector tests.
- Normalizer tests.
- Hashing tests.
- Change detection tests.
- Memory record builder and router tests.
- Sink router and sink adapter tests.
- Runtime mode and scheduler tests.
- In-process e2e API-to-sink flow tests.

## Current result

Latest run:

```text
40 passed, 1 skipped
```

## Constraints

- Tests do not require live Kubernetes by default.
- Sink adapter tests use fake clients.
- Live e2e is opt-in through `RUN_LIVE_E2E=true`.
