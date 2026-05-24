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

## Constraints

- Namespace-scoped deployment.
- No ClusterRole or ClusterRoleBinding.
- Secret values are referenced through Kubernetes Secret env vars.
