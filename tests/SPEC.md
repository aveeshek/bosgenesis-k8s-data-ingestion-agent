# Tests Specification

## Role

The `tests` directory will hold future tests and test fixtures.

## Required test categories

- Unit tests for normalizers, hashing, change detection, and config validation.
- Contract tests for MCP allowlist and denylist behavior.
- Integration tests for sink adapters with mocked services.
- API tests for health, scan run, latest scan, and effective config.
- Deployment validation tests for Helm rendering and Kubernetes manifests.

## Constraints

- Tests must not require live Kubernetes by default.
- Tests must not call real sink services unless explicitly configured.

