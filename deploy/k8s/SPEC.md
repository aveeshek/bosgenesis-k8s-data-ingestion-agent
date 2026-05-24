# Kubernetes Manifests Specification

## Role

This directory will contain raw Kubernetes manifests or kustomize overlays after the design is approved.

## Planned resource specs

- Deployment.
- Service.
- ConfigMap.
- Secret example or secret reference.
- ServiceAccount.
- Role.
- RoleBinding.
- NetworkPolicy.
- Optional Ingress.

## Constraints

- Namespace-scoped only.
- No ClusterRole or ClusterRoleBinding.
- No direct access to Kubernetes Secrets from the agent.

