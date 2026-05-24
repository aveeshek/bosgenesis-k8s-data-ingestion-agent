# Agent Helm Chart Specification

## Role

This chart will deploy `bosgenesis-k8s-data-ingestion-agent` into the BOS Genesis namespace.

## Planned chart areas

- Chart metadata.
- Default values.
- Deployment template.
- Service template.
- ConfigMap template.
- Secret reference template.
- ServiceAccount and RBAC templates.
- NetworkPolicy template.
- Optional Ingress template.
- Notes and validation helpers.

## Constraints

- Do not include executable templates until implementation is approved.
- Keep mutating cluster-scoped resources out of chart scope.

