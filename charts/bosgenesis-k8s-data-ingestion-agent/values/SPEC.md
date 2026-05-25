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
- MCP service URLs and upstream Host header overrides
- optional secret values
- service
- ingress
- resources
- pod security context
- optional private credentials override through `values.credentials.yaml`

## Default runtime

The default chart runs `runtimeMode: service`, which starts API and scheduler together.

## Default ingress

Ingress is enabled by default with host `data-ingestion-agent.bosgenesis.local`.

## Credentials override

Use `values.credentials.example.yaml` as the template for local private credentials. The copied `values.credentials.yaml` file should set `secret.create=true`, `secret.postgresDsn`, and `secret.clickhousePassword` when PostgreSQL and ClickHouse sinks are enabled.
