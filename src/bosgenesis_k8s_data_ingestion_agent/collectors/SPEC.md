# Collectors Module Specification

## Role

Collectors will gather raw Kubernetes and Helm bundles through MCP clients.

## Responsibilities

- Collect namespace summaries and resource lists.
- Collect Helm release status, history, values, and manifests according to request options.
- Collect pod logs only when enabled and bounded.
- Preserve raw payloads for downstream normalization.

## Collector types

- Namespace collector.
- Workload collector.
- Event collector.
- Log collector.
- Helm release collector.

## Constraints

- Collectors must not persist data.
- Collectors must not compute final content hashes.
- Collectors must not call non-allowlisted MCP tools.

