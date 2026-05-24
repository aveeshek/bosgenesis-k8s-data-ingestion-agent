# Validation Playbook Specification

## Role

This directory will document post-deployment checks.

## Responsibilities

- Validate `/health`.
- Trigger a dry on-demand scan.
- Confirm read-only MCP calls.
- Confirm enabled sink writes.
- Confirm traces and logs.
- Confirm no Kubernetes or Helm mutations occur.

