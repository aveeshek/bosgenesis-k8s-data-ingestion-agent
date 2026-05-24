# AGENTS.md - BOS Genesis K8s Data Ingestion Agent

## Project purpose

This repository will implement `bosgenesis-k8s-data-ingestion-agent`, a read-only ETL and evidence-ingestion agent for BOS Genesis Kubernetes operational state.

The agent will periodically and on demand collect Kubernetes and Helm state through existing BOS Genesis MCP servers, normalize observations, detect meaningful changes with stable hashes, and route changed records to configured analytical, memory, cache, and observability sinks.

## Hard safety rules

- Operate inside the configured namespace only. The default namespace is `bosgenesis`.
- Use existing MCP read tools for Kubernetes and Helm inspection.
- Never call raw `kubectl` or raw `helm` from the agent runtime.
- Never mutate Kubernetes or Helm state.
- Never collect Kubernetes Secrets or secret-like values.
- Never perform remediation, alerting, anomaly detection, or MoP execution in this agent.
- Keep Letta integration disabled by default.
- Treat logs as optional, bounded, and disabled unless explicitly requested.
- Every scan must have `run_id`, `correlation_id`, structured status, and trace context.

## Required root folders

- `codex`
- `knowledge-base`
- `memory`
- `playbook`
- `skills`

## Implementation posture

This scaffold intentionally contains specification files only. Future code should be added only after the module contracts in this repository are reviewed and accepted.

