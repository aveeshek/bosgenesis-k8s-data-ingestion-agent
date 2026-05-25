# Agent Helm Chart Specification

## Implemented status

This chart deploys `bosgenesis-k8s-data-ingestion-agent` into the BOS Genesis namespace.

## Implemented chart areas

- `Chart.yaml`
- `values.yaml`
- `values.credentials.example.yaml`
- helper templates
- ConfigMap template
- optional Secret template
- ServiceAccount template
- Deployment template
- Service template
- default-enabled configurable Ingress template
- NOTES template

## Constraints

- No cluster-scoped resources.
- No ClusterRole or ClusterRoleBinding.
- Secret creation is optional.
- Real credential values must be supplied through a private override file or external secret, not committed defaults.
