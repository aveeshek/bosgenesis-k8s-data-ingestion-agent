# Fixtures Specification

## Role

Fixtures will hold sanitized example MCP payloads for deterministic tests.

## Responsibilities

- Provide Kubernetes namespace summary payloads.
- Provide pod, deployment, service, PVC, ingress, and event payloads.
- Provide Helm release, status, history, values, and manifest payloads.
- Include changed and unchanged comparison scenarios.

## Constraints

- No secrets.
- No production payloads unless sanitized.

