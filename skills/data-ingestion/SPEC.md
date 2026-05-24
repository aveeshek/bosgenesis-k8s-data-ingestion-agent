# Data Ingestion Skill Specification

## Role

This future skill will help agents request namespace scans and interpret returned summaries.

## Responsibilities

- Call the on-demand scan endpoint or optional MCP tool.
- Request bounded logs only when needed.
- Prefer summaries for routine workflows.
- Preserve correlation IDs for traceability.

