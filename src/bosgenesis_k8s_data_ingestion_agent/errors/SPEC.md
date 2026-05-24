# Errors Module Specification

## Role

The errors module will define domain-specific exceptions and failure summaries.

## Responsibilities

- Represent MCP transport failures.
- Represent denied tool calls.
- Represent normalization failures.
- Represent sink failures.
- Represent partial scan failures.
- Preserve enough context for traces without leaking secrets.

