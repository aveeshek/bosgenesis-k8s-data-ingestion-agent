# Kubernetes Base Specification

## Implemented status

The current implementation uses flat manifests in `deploy/k8s` instead of a `base` directory.

## Current base resources

- Common labels and selectors are in each manifest.
- Deployment security context runs as non-root UID `10001`.
- ConfigMap holds non-secret runtime settings.
- Secret example documents required secret variables.

## Future option

This directory can become a kustomize base if environment overlays are added later.
