# Source Tree Specification

## Role

The `src` tree will contain the future Python package for the data ingestion agent.

## Package boundary

All runtime code should live under `src/bosgenesis_k8s_data_ingestion_agent` once implementation begins.

## Design principles

- Keep modules small and independently testable.
- Depend inward on domain contracts, not outward on concrete sink clients.
- Keep external integrations behind explicit adapters.
- Ensure read-only Kubernetes and Helm behavior is enforced in client policy, not just documentation.

