# Deployment Specification

## Implemented status

The `deploy` directory now contains raw Kubernetes deployment assets.

## Implemented resources

- Namespace.
- ServiceAccount.
- ConfigMap.
- Secret example.
- Deployment.
- Service.
- Optional Ingress.
- Kustomization.

## Defaults

- Namespace: `bosgenesis`.
- Runtime mode: `service`.
- Scan interval: `3600` seconds.
- API port: `8080`.
- Image: `bosgenesis-k8s-data-ingestion-agent:0.0.1`.

## Not implemented yet

- NetworkPolicy.
- Role/RoleBinding; the agent calls MCP services and does not directly call Kubernetes API.
