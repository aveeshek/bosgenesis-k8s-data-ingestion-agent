# BOS Genesis K8s Data Ingestion Agent

`bosgenesis-k8s-data-ingestion-agent` is a read-only ETL agent for collecting BOS Genesis Kubernetes and Helm operational state through existing MCP servers.

The agent normalizes observations, computes stable content hashes, detects changes, routes records to optional sinks, and emits detailed structured logs. It exposes both REST endpoints and a Streamable HTTP MCP endpoint at `/mcp`.

## Safety posture

- Read-only Kubernetes and Helm collection.
- MCP allowlists and mutation denylists.
- No raw `kubectl` or `helm` runtime execution.
- No remediation, alerting, anomaly detection, or MoP execution.
- Optional bounded pod log collection only.

## Runtime Modes and Scheduler

The agent supports three runtime modes:

```bash
bosgenesis-k8s-data-ingestion-agent api
bosgenesis-k8s-data-ingestion-agent scheduler
bosgenesis-k8s-data-ingestion-agent service
```

- `api`: starts only the REST API for on-demand scans.
- `scheduler`: starts only the periodic scanner.
- `service`: starts both API and scheduler. This is the default deployment mode.

The scheduler is controlled with:

| Variable | Default | Purpose |
|---|---:|---|
| `AGENT_SCAN_INTERVAL_SECONDS` | `3600` | Periodic scan interval. `3600` means every 1 hour. |
| `AGENT_RUN_ON_STARTUP` | `true` | Run one scan immediately when the scheduler starts. |

To disable the cron-like scheduled scan but keep on-demand API, run in `api` mode:

```yaml
args: ["api"]
```

For Helm:

```bash
helm upgrade --install bosgenesis-k8s-data-ingestion-agent \
  charts/bosgenesis-k8s-data-ingestion-agent \
  --namespace bosgenesis \
  --set runtimeMode=api
```

To keep the scheduler but change the interval to every 30 minutes:

```bash
kubectl -n bosgenesis patch configmap bosgenesis-k8s-data-ingestion-agent-config \
  --type merge \
  -p '{"data":{"AGENT_SCAN_INTERVAL_SECONDS":"1800"}}'
kubectl -n bosgenesis rollout restart deployment/bosgenesis-k8s-data-ingestion-agent
```

## Sink Configuration

Sinks are enabled and disabled through environment variables. In raw Kubernetes deployment, edit:

```text
deploy/k8s/configmap.yaml
```

For Helm deployment, edit or override:

```text
charts/bosgenesis-k8s-data-ingestion-agent/values.yaml
```

### Enable/Disable Variables

| Sink | Raw env var | Helm value | Default |
|---|---|---|---|
| PostgreSQL | `POSTGRES_ENABLED` | `config.postgresEnabled` | `true` |
| ClickHouse | `CLICKHOUSE_ENABLED` | `config.clickhouseEnabled` | `true` |
| Qdrant | `QDRANT_ENABLED` | `config.qdrantEnabled` | `true` |
| Redis | `REDIS_ENABLED` | `config.redisEnabled` | `true` |
| Stdout | `STDOUT_ENABLED` | `config.stdoutEnabled` | `false` |

Example: disable Qdrant and Redis with raw Kubernetes:

```bash
kubectl -n bosgenesis patch configmap bosgenesis-k8s-data-ingestion-agent-config \
  --type merge \
  -p '{"data":{"QDRANT_ENABLED":"false","REDIS_ENABLED":"false"}}'
kubectl -n bosgenesis rollout restart deployment/bosgenesis-k8s-data-ingestion-agent
```

Example: disable Qdrant and Redis with Helm:

```bash
helm upgrade --install bosgenesis-k8s-data-ingestion-agent \
  charts/bosgenesis-k8s-data-ingestion-agent \
  --namespace bosgenesis \
  --set config.qdrantEnabled=false \
  --set config.redisEnabled=false
```

`playbook/deploy.sh` prompts for sink selection when run interactively. Press Enter to keep the default set enabled:

```text
postgres clickhouse qdrant redis
```

You can also run non-interactively:

```bash
SINKS_ENABLED="postgres clickhouse" ./playbook/deploy.sh
SINKS_ENABLED="postgres,clickhouse,qdrant" ./playbook/deploy.sh
SINKS_ENABLED=none ./playbook/deploy.sh
ENABLE_SINK_PROMPT=false POSTGRES_ENABLED=true CLICKHOUSE_ENABLED=false QDRANT_ENABLED=false REDIS_ENABLED=false ./playbook/deploy.sh
```

`SINKS_ENABLED=all` keeps the default sink set. `stdout` is available as an explicit selection but is disabled by default.

### Sink Connection Settings

| Sink | Important settings |
|---|---|
| PostgreSQL | `POSTGRES_DSN` secret env var |
| ClickHouse | `CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_DATABASE`, `CLICKHOUSE_PASSWORD` |
| Qdrant | `QDRANT_URL`, `QDRANT_COLLECTION`, `QDRANT_VECTOR_SIZE`, `QDRANT_API_KEY` |
| Redis | `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_KEY_PREFIX`, `REDIS_PASSWORD` |

Secret values should live in `bosgenesis-k8s-data-ingestion-agent-secret`, not in ConfigMap.

With the default install, PostgreSQL and ClickHouse are enabled. For Helm-based fresh installs, put credentials in a private values override:

```bash
cp charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.example.yaml \
  charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml
```

Edit `values.credentials.yaml` and set:

```yaml
secret:
  create: true
  postgresDsn: "postgresql://USER:PASSWORD@postgresql.bosgenesis.svc.cluster.local:5432/DATABASE"
  clickhousePassword: "PASSWORD"
```

Then install with:

```bash
./playbook/deploy.sh
```

`deploy.sh` defaults to Helm and automatically loads `charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml` when the file exists. The file is ignored by Git. Use the actual database, user, and password values from your cluster. If you do not want these sinks yet, disable them with `POSTGRES_ENABLED=false` or `CLICKHOUSE_ENABLED=false`.

The agent calls the upstream MCP services through in-cluster service URLs and sends the expected BOS Genesis host headers:

```yaml
K8S_MCP_URL: "http://bosgenesis-k8s-inspector-mcp.bosgenesis.svc.cluster.local:8080/mcp"
K8S_MCP_HOST_HEADER: "k8s-inspector.bosgenesis.local"
HELM_MCP_URL: "http://bosgenesis-helm-manager-mcp.bosgenesis.svc.cluster.local:8080/mcp"
HELM_MCP_HOST_HEADER: "helm-manager.bosgenesis.local"
```

## Langfuse Tracing

Langfuse tracing is enabled by default and can be disabled through config.

Non-secret runtime settings live in ConfigMap or Helm values:

```text
LANGFUSE_ENABLED=true
LANGFUSE_BASE_URL=http://langfuse-web.bosgenesis.svc.cluster.local:3000
```

Secret keys must live in `bosgenesis-k8s-data-ingestion-agent-secret` or Helm credentials values:

```text
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

Disable tracing:

```bash
LANGFUSE_ENABLED=false ./playbook/deploy.sh
```

For Helm:

```bash
helm upgrade --install bosgenesis-k8s-data-ingestion-agent \
  charts/bosgenesis-k8s-data-ingestion-agent \
  --namespace bosgenesis \
  --set config.langfuseEnabled=false
```

When credentials or the Langfuse SDK are unavailable, the agent logs a warning and continues without tracing. Successful traces add `trace_ids.langfuse` to scan summaries.

## Langflow Architecture View

A visualization-only Langflow graph is available at `langflow/data-ingestion-agent-architecture.json`.

Import it into Langflow to view the high-level data flow from Codex/GPT/agents through the agent MCP endpoint, internal workflow, existing MCP tools, storage sinks, and observability sinks. The graph is documentation-only and does not execute calls or store credentials.

## On-Demand Scan

Port-forward:

```bash
kubectl -n bosgenesis port-forward svc/bosgenesis-k8s-data-ingestion-agent 8080:8080
```

Run a scan:

```bash
curl -X POST http://127.0.0.1:8080/scan/run \
  -H "Content-Type: application/json" \
  -d '{"trigger_type":"manual","namespace":"bosgenesis"}'
```

## MCP Endpoint

The same FastAPI service exposes remote MCP at:

```text
http://data-ingestion-agent.bosgenesis.local/mcp
```

Initial MCP tools:

```text
data_ingestion_health
data_ingestion_run_scan
data_ingestion_latest_scan
data_ingestion_effective_config
```

Codex config:

```toml
[mcp_servers.data_ingestion_agent]
enabled = true
url = "http://data-ingestion-agent.bosgenesis.local/mcp"
startup_timeout_sec = 20
tool_timeout_sec = 180
default_tools_approval_mode = "prompt"

[mcp_servers.data_ingestion_agent.tools.data_ingestion_run_scan]
approval_mode = "prompt"
```

## Deploy and Uninstall

Deploy with the bundled playbook:

```bash
chmod +x playbook/deploy.sh
./playbook/deploy.sh
```

The default deploy method is Helm. To force raw manifests:

```bash
DEPLOY_METHOD=kustomize ./playbook/deploy.sh
```

Ingress is enabled by default and exposes:

```text
data-ingestion-agent.bosgenesis.local
```

To deploy without ingress:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

Ingress is enabled by default through `ingress.enabled=true` in `values.yaml`. Disable it with:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

Uninstall the default Helm deployment:

```bash
chmod +x playbook/uninstaller.sh
./playbook/uninstaller.sh
```

Uninstall raw Kubernetes resources instead:

```bash
DEPLOY_METHOD=kustomize ./playbook/uninstaller.sh
```

The uninstaller removes the Deployment, Service, Ingress, ConfigMap, and ServiceAccount for `bosgenesis-k8s-data-ingestion-agent`. It does not delete secrets, the shared `bosgenesis` namespace, imported containerd images, or copied image tar files unless explicitly requested.

Optional cleanup flags:

```bash
DELETE_SECRET=true ./playbook/uninstaller.sh
DELETE_REMOTE_IMAGE=true DELETE_REMOTE_TAR=true ./playbook/uninstaller.sh
```

Only use namespace deletion when the namespace is dedicated to this agent:

```bash
DELETE_NAMESPACE=true ./playbook/uninstaller.sh
```
