# Playbook Folder Specification

## Implemented status

The playbook folder now contains deployment automation and operator documentation.

## Implemented assets

- `deploy.sh`: build, save, transfer, containerd import, apply/helm deploy, rollout status.
- `deployment/DEPLOYMENT.md`: deployment and verification guide.

## Responsibilities

- Deploy through the cluster containerd import workflow.
- Support raw kustomize manifests or Helm deployment.
- Support optional ingress.
- Document API health and on-demand scan checks.
