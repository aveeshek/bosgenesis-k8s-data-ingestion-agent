# Collectors Module Specification

## Implemented status

Collectors gather raw Kubernetes and Helm bundles through allowlisted MCP clients.

## Implemented collectors

- `KubernetesCollector`
- `HelmCollector`

## Kubernetes collection

Collects:

- namespace summary
- pods
- deployments
- statefulsets
- services
- ingresses
- PVCs
- events
- optional bounded pod logs when `include_logs=true`

## Helm collection

Collects:

- release list
- release status
- release history
- optional values when `include_values=true`
- optional manifest when `include_manifests=true`
- repository list

## Constraints

- Collectors do not persist data.
- Collectors do not compute hashes.
- Collectors can only call tools accepted by MCP client policy.
