# BOS Genesis K8s Data Ingestion Agent

`bosgenesis-k8s-data-ingestion-agent` is a read-only ETL agent for collecting BOS Genesis Kubernetes and Helm operational state through existing MCP servers.

The agent normalizes observations, computes stable content hashes, detects changes, routes records to optional sinks, and emits detailed structured logs.

## Safety posture

- Read-only Kubernetes and Helm collection.
- MCP allowlists and mutation denylists.
- No raw `kubectl` or `helm` runtime execution.
- No remediation, alerting, anomaly detection, or MoP execution.
- Optional bounded pod log collection only.

