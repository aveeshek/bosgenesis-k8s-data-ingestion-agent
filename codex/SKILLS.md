---
name: bosgenesis-k8s-data-ingestion-agent
description: Use when Codex needs to inspect, operate, test, deploy, or run the read-only BOS Genesis Kubernetes data ingestion agent through `data_ingestion_agent`, including health, redacted effective config, latest scan summaries, and explicit on-demand scans that collect Kubernetes/Helm observations into configured sinks.
---

# BOS Genesis K8s Data Ingestion Agent

Use the `data_ingestion_agent` MCP server for read-only BOS Genesis Kubernetes and Helm evidence ingestion. The agent scans through existing MCP servers, normalizes observations, computes stable hashes, detects changes, writes configured sinks, and exposes REST plus `/mcp`.

## MCP Server

```toml
[mcp_servers.data_ingestion_agent]
url = "http://data-ingestion-agent.bosgenesis.local/mcp"
```

## Safety Rules

- Keep runtime behavior read-only for Kubernetes and Helm.
- Do not add raw `kubectl` or `helm` execution to the runtime.
- Do not collect Kubernetes Secrets or secret-like values.
- Do not add remediation, anomaly alerting, MoP execution, Helm mutation, or Kubernetes mutation.
- Treat `data_ingestion_run_scan` as active/expensive; ask before running it unless the user explicitly requested a scan.
- Keep live e2e tests opt-in.
- Do not commit credentials, kubeconfigs, tokens, passwords, or real DSNs.

## MCP Workflow

1. Call `data_ingestion_health`.
2. Call `data_ingestion_effective_config` when validating redacted runtime config.
3. Call `data_ingestion_latest_scan` before triggering a new scan.
4. Call `data_ingestion_run_scan` only when the user requested a fresh scan.
5. Summarize scan status, namespace, observed resources, sink writes, trace IDs, and redaction status.

## Tool Map

- `data_ingestion_health`
- `data_ingestion_run_scan`
- `data_ingestion_latest_scan`
- `data_ingestion_effective_config`

## REST Reference

```text
Base URL: http://data-ingestion-agent.bosgenesis.local
Health:   GET /health
Run scan: POST /scan/run
Latest:   GET /scan/latest
MCP:      POST /mcp
```

Example scan request:

```json
{
  "trigger_type": "manual",
  "namespace": "bosgenesis",
  "include_logs": false,
  "correlation_id": "optional-correlation-id"
}
```
