# Deployment Playbook Specification

## Implemented status

This directory contains a concrete deployment guide.

## Implemented guide coverage

- Docker build.
- Docker save.
- SCP tar to cluster node.
- containerd image import with `ctr`.
- Raw manifest deployment through `kubectl apply -k`.
- Helm deployment through `helm upgrade --install`.
- Optional ingress.
- Rollout and service verification.
- API health and on-demand scan checks.
