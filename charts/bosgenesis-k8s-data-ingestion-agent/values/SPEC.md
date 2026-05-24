# Helm Values Specification

## Implemented status

Helm values are implemented in `values.yaml`.

## Implemented value groups

- replica count
- image repository, tag, pull policy
- runtime mode
- namespace override
- service account
- non-secret config
- optional secret values
- service
- ingress
- resources
- pod security context

## Default runtime

The default chart runs `runtimeMode: service`, which starts API and scheduler together.
