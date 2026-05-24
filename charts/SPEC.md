# Helm Charts Specification

## Implemented status

The `charts` directory contains a Helm v3 application chart for the agent.

## Implemented responsibilities

- Package Deployment, Service, ConfigMap, ServiceAccount, optional Secret, and optional Ingress.
- Configure runtime mode, image repository/tag, scheduler interval, MCP endpoints, sinks, and resources through values.
- Keep secret values behind optional Kubernetes Secret creation or external secret reference.
