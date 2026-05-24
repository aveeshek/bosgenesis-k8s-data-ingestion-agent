# Contract Tests Specification

## Role

Contract tests will protect module boundaries and safety requirements.

## Responsibilities

- Assert Kubernetes and Helm mutation tools cannot be called.
- Assert secret-like fields are redacted.
- Assert scan summaries keep required IDs and counts.
- Assert sink failure policy is respected.

