# Helm Templates Specification

## Implemented status

This directory contains executable Helm templates.

## Implemented templates

- `_helpers.tpl`
- `configmap.yaml`
- `secret.yaml`
- `serviceaccount.yaml`
- `deployment.yaml`
- `service.yaml`
- `ingress.yaml`
- `NOTES.txt`

## Responsibilities

- Render namespace-scoped resources.
- Support optional Secret and Ingress.
- Use consistent labels.
- Pass runtime mode and environment settings to the container.
