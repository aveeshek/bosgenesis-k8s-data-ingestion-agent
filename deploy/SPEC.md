# Deployment Specification

## Role

The `deploy` directory will hold Kubernetes deployment specifications once implementation begins.

## Responsibilities

- Define namespace-scoped deployment resources.
- Keep runtime configuration externalized.
- Use least-privilege service account and RBAC.
- Support optional ingress.
- Support network policies for MCP and sink connectivity.

## No-code constraint

No Kubernetes YAML is included in the initial scaffold.

