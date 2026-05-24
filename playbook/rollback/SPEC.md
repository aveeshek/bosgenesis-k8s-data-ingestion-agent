# Rollback Playbook Specification

## Implemented status

Rollback is not automated yet, but deployment assets support standard Kubernetes and Helm rollback commands.

## Supported rollback paths

- Helm: `helm rollback`.
- Raw manifests: `kubectl rollout undo deployment/bosgenesis-k8s-data-ingestion-agent -n bosgenesis`.
- Sink disablement through ConfigMap/env changes.

## Verification

- `kubectl rollout status`
- `GET /health`
- `POST /scan/run`
