# Security Module Specification

## Role

The security module will define runtime protections for read-only behavior and sensitive-data handling.

## Responsibilities

- Enforce MCP tool allowlists and denylists.
- Redact sensitive fields before sink writes and API responses.
- Validate namespace scope.
- Provide API authentication and authorization hooks if required.

## Denied behavior

- Kubernetes mutation.
- Helm mutation.
- Secret collection.
- Cross-namespace scanning unless explicitly configured in a future approved design.

