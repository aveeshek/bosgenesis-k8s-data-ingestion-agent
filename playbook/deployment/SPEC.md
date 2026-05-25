# Deployment Playbook Specification

## Implemented status

This directory contains a concrete deployment guide.

## Implemented guide coverage

- Docker build.
- Docker save.
- SCP tar to cluster node.
- containerd image import with `ctr`.
- Default Helm deployment through `helm upgrade --install`.
- Auto-loaded private values override for credentials.
- Raw manifest deployment through `kubectl apply -k` when explicitly requested.
- Default-enabled ingress with explicit disablement option.
- Rollout and service verification.
- API health and on-demand scan checks.
