# Agent Helm Chart Specification

## Implemented status

This chart deploys `bosgenesis-k8s-data-ingestion-agent` into the BOS Genesis namespace.

## Implemented chart areas

- `Chart.yaml`
- `values.yaml`
- helper templates
- ConfigMap template
- optional Secret template
- ServiceAccount template
- Deployment template
- Service template
- optional Ingress template
- NOTES template

## Constraints

- No cluster-scoped resources.
- No ClusterRole or ClusterRoleBinding.
- Secret creation is optional.
