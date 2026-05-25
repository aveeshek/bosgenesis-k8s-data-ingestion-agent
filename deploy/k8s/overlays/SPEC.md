# Kubernetes Overlays Specification

## Implemented status

No overlays are implemented yet.

## Current customization path

- Edit raw manifests directly for immediate use.
- Use Helm values for repeatable environment customization.
- Use `playbook/deploy.sh` variables for image tag, target node, deploy method, and ingress enablement.

## Future responsibilities

- Add dev/stage/prod overlays if raw-manifest deployments need environment-specific patches.
