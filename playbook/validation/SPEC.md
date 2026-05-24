# Validation Playbook Specification

## Implemented status

Validation is documented in `playbook/deployment/DEPLOYMENT.md` and covered by tests.

## Implemented validation commands

- `kubectl rollout status`
- `kubectl get pod`
- `kubectl get svc`
- port-forward service
- `GET /health`
- `POST /scan/run`

## Test validation

- Unit tests cover module behavior.
- In-process e2e tests cover API-to-sink flow.
- Live e2e remains opt-in.
