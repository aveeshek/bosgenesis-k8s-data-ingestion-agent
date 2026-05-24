# Security Module Specification

## Implemented status

The security module implements payload redaction and namespace validation helpers.

## Implemented responsibilities

- Recursively redact secret-like keys.
- Validate namespace against an allowed namespace.

## Read-only enforcement

MCP tool allowlists and mutation denylists are implemented in `mcp_clients.policy`.

## Denied behavior

- Kubernetes mutation.
- Helm mutation.
- secret collection.
- cross-namespace scanning unless a future approved design explicitly changes scope.
