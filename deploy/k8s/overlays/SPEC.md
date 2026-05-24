# Kubernetes Overlays Specification

## Role

Overlays will customize base manifests for local, development, staging, or production environments.

## Responsibilities

- Override replica counts.
- Override resource requests and limits.
- Override ingress hostnames.
- Override non-secret endpoint settings.

