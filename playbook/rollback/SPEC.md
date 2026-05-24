# Rollback Playbook Specification

## Role

This directory will document rollback strategy.

## Responsibilities

- Roll back Helm release or Kubernetes deployment.
- Preserve persisted analytical data.
- Disable problematic sinks without redeploying code when possible.
- Verify service health after rollback.

