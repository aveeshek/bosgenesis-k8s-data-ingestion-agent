# Playbook Folder Specification

## Implemented status

The playbook folder now contains deployment automation and operator documentation.

## Implemented assets

- `deploy.sh`: build, save, transfer, containerd import, apply/helm deploy, rollout status.
- `deployment/DEPLOYMENT.md`: deployment and verification guide.

## Responsibilities

- Deploy through the cluster containerd import workflow.
- Default to Helm deployment while still supporting raw kustomize manifests.
- Enable ingress by default while supporting explicit disablement.
- Auto-load `values.credentials.yaml` when present and support `HELM_VALUES_FILE` for private Helm credential overrides.
- Document API health and on-demand scan checks.
