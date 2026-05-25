# Kubernetes Manifests Specification

## Implemented status

This directory contains raw Kubernetes manifests and a kustomization.

## Implemented resource specs

- `namespace.yaml`
- `serviceaccount.yaml`
- `configmap.yaml`
- `secret.example.yaml`
- `deployment.yaml`
- `service.yaml`
- `ingress.yaml`
- `kustomization.yaml`

## Runtime behavior

The Deployment starts:

```text
bosgenesis-k8s-data-ingestion-agent service
```

This enables the API and hourly scheduler together.

Ingress is included in the default kustomization and exposes `data-ingestion-agent.bosgenesis.local`.

## Constraints

- Namespace-scoped deployment.
- No ClusterRole or ClusterRoleBinding.
- Secret values are referenced through Kubernetes Secret env vars.
