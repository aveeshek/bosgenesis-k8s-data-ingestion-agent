# BOS Genesis K8s Data Ingestion Agent Skill

## When to use this skill

Use this skill when working on `bosgenesis-k8s-data-ingestion-agent`, including implementation, testing, deployment, sink initialization, Kubernetes packaging, Helm packaging, or operational validation.

This agent is a read-only ETL and evidence-ingestion service for BOS Genesis Kubernetes and Helm state. It scans through existing MCP servers, normalizes observations, computes stable hashes, detects changes, writes configured sinks, and exposes an on-demand REST API plus a remote MCP endpoint at `/mcp`.

## Safety rules

- Keep the runtime read-only for Kubernetes and Helm.
- Do not add raw `kubectl` or `helm` execution to the agent runtime.
- Do not collect Kubernetes Secrets or secret-like values.
- Do not add remediation, anomaly alerting, MoP execution, Helm mutation, or Kubernetes mutation.
- Preserve MCP read allowlists and mutation denylists.
- Keep Letta disabled unless explicitly requested and configuration-gated.
- Keep live e2e tests opt-in.
- Do not commit credentials, kubeconfigs, tokens, passwords, or real DSNs.
- Keep Langfuse tracing enabled by default, but config-gated with `LANGFUSE_ENABLED=false`.

## Important paths

- Runtime package: `src/bosgenesis_k8s_data_ingestion_agent`
- API: `src/bosgenesis_k8s_data_ingestion_agent/api`
- Scheduler: `src/bosgenesis_k8s_data_ingestion_agent/scheduler`
- Orchestrator: `src/bosgenesis_k8s_data_ingestion_agent/core`
- MCP clients: `src/bosgenesis_k8s_data_ingestion_agent/mcp_clients`
- Collectors: `src/bosgenesis_k8s_data_ingestion_agent/collectors`
- Normalizers: `src/bosgenesis_k8s_data_ingestion_agent/normalizers`
- Sinks: `src/bosgenesis_k8s_data_ingestion_agent/sinks`
- Memory abstraction: `src/bosgenesis_k8s_data_ingestion_agent/memory`
- Raw sink initialization: `sinks`
- Kubernetes manifests: `deploy/k8s`
- Helm chart: `charts/bosgenesis-k8s-data-ingestion-agent`
- Deployment script: `playbook/deploy.sh`
- E2E tests: `tests/e2e`

## Standard validation

Run these after code changes:

```bash
python -m pytest
python -m ruff check .
```

Run in-process e2e tests:

```bash
python -m pytest tests/e2e
```

Live e2e is opt-in only:

```bash
RUN_LIVE_E2E=true \
AGENT_BASE_URL=http://data-ingestion-agent.bosgenesis.local \
python -m pytest tests/e2e -m live_e2e
```

## Runtime modes

```bash
bosgenesis-k8s-data-ingestion-agent api
bosgenesis-k8s-data-ingestion-agent scheduler
bosgenesis-k8s-data-ingestion-agent service
```

Default deployment mode is `service`, which starts both REST API and hourly scheduler.

## Deployment workflow

The target cluster may require image import through containerd. Use:

```bash
chmod +x playbook/deploy.sh
./playbook/deploy.sh
```

Important defaults:

- Namespace: `bosgenesis`
- Image: `bosgenesis-k8s-data-ingestion-agent:0.0.1`
- Deployment: `bosgenesis-k8s-data-ingestion-agent`
- Container: `app`
- Remote node: `taieuser@10.99.52.165`

Ingress is enabled by default:

```bash
./playbook/deploy.sh
```

Disable ingress:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

Use Helm:

```bash
DEPLOY_METHOD=helm ./playbook/deploy.sh
```

## On-demand usage

Port-forward:

```bash
kubectl -n bosgenesis port-forward svc/bosgenesis-k8s-data-ingestion-agent 8080:8080
```

Health:

```bash
curl http://127.0.0.1:8080/health
```

Run scan:

```bash
curl -X POST http://127.0.0.1:8080/scan/run \
  -H "Content-Type: application/json" \
  -d '{"trigger_type":"manual","namespace":"bosgenesis"}'
```

## Remote MCP usage

The deployed MCP endpoint is:

```text
http://data-ingestion-agent.bosgenesis.local/mcp
```

Use these tools:

- `data_ingestion_health`
- `data_ingestion_run_scan`
- `data_ingestion_latest_scan`
- `data_ingestion_effective_config`

Treat `data_ingestion_run_scan` as an expensive/active operation. Ask before running it unless the user explicitly requested a scan.

## Current memory model

The agent has a thin agentic memory abstraction:

- Session memory: scan summaries.
- Episodic memory: observed change events.
- Semantic memory: compact operational facts.

`MemoryRecordBuilder` creates memory records. `MemoryRouter` routes them to memory-capable sinks. `QdrantSink` supports `write_memory()`.

## Langfuse tracing

Langfuse tracing is enabled by default when credentials are provided:

- `LANGFUSE_ENABLED=true`
- `LANGFUSE_BASE_URL=http://langfuse-web.bosgenesis.svc.cluster.local:3000`
- `LANGFUSE_PUBLIC_KEY` from Secret
- `LANGFUSE_SECRET_KEY` from Secret

Disable with:

```bash
LANGFUSE_ENABLED=false ./playbook/deploy.sh
```

Scan summaries include `trace_ids.langfuse` when tracing is active.
