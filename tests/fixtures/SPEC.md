# Fixtures Specification

## Implemented status

Test fixtures are currently inline inside unit and e2e tests.

## Current fixture coverage

- Kubernetes pods and deployments.
- Empty service/statefulset/ingress/PVC/event payloads.
- Helm release, status, history, and repo list payloads.
- Changed and unchanged comparison scenarios.

## Future option

Move reusable sanitized payloads into this directory when they become large or shared across many tests.
