# Contract Tests Specification

## Implemented status

Contract-style assertions are currently covered by focused unit tests.

## Implemented protections

- MCP mutation tools are denied.
- Unknown tools such as secret listing are denied.
- Secret-like fields are redacted.
- Scan summaries carry IDs, status, counts, and sink names.
- Memory records preserve memory type, run context, entity identity, and metadata.
- Sink router validates strict/non-strict behavior through sink tests.

## Future option

Dedicated contract test files can be split out if the public interfaces expand.
