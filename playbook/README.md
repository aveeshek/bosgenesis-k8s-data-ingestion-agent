# Deploy Script README

This folder contains deployment helpers for `bosgenesis-k8s-data-ingestion-agent`.

`deploy.sh` is designed for the BOS Genesis cluster flow where Docker images are built locally, saved as a tar file, copied to a Kubernetes node, imported into containerd with `ctr`, and then rolled out with `kubectl`.

`uninstaller.sh` removes this agent's Kubernetes or Helm deployment resources and can optionally clean secrets and remote image artifacts.

## Default Deployment

From the repository root:

```bash
chmod +x playbook/deploy.sh
./playbook/deploy.sh
```

Default values:

| Setting | Default |
|---|---|
| Namespace | `bosgenesis` |
| Deployment | `bosgenesis-k8s-data-ingestion-agent` |
| Container | `app` |
| Image | `bosgenesis-k8s-data-ingestion-agent:0.0.1` |
| Remote node | `taieuser@10.99.52.165` |
| Deploy method | `helm` |
| Ingress | `enabled` |
| Helm values override | auto-loads `charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml` if present |

## What The Script Does

1. Builds the Docker image.
2. Saves the image to a tar file.
3. Copies the tar file to the target node.
4. Imports the image into containerd:

```bash
sudo ctr -n k8s.io images import /tmp/bosgenesis-k8s-data-ingestion-agent-0.0.1.tar
```

5. Applies Kubernetes manifests or Helm chart.
6. Updates the Deployment image.
7. Waits for rollout completion.
8. Prints pods and service status.

## Common Commands

Deploy a specific tag:

```bash
IMAGE_TAG=0.0.2 ./playbook/deploy.sh
```

Deploy without ingress:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

Deploy with the default Helm method:

```bash
./playbook/deploy.sh
```

When present, this private credentials file is loaded automatically:

```bash
charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml
```

Deploy with Helm and no ingress:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

Deploy with raw manifests:

```bash
DEPLOY_METHOD=kustomize ./playbook/deploy.sh
```

Deploy with an explicit alternate Helm values file:

```bash
HELM_VALUES_FILE=/path/to/private-values.yaml ./playbook/deploy.sh
```

## MCP Service Hostnames

The agent calls MCP services through ClusterIP DNS while sending the allowed ingress hostname in the HTTP `Host` header:

```yaml
K8S_MCP_URL: "http://bosgenesis-k8s-inspector-mcp.bosgenesis.svc.cluster.local:8080/mcp"
K8S_MCP_HOST_HEADER: "k8s-inspector.bosgenesis.local"
HELM_MCP_URL: "http://bosgenesis-helm-manager-mcp.bosgenesis.svc.cluster.local:8080/mcp"
HELM_MCP_HOST_HEADER: "helm-manager.bosgenesis.local"
```

Use another node:

```bash
REMOTE_USER=taieuser REMOTE_HOST=10.99.52.165 ./playbook/deploy.sh
```

Skip image build and reuse an existing local tar:

```bash
SKIP_BUILD=true ./playbook/deploy.sh
```

Skip image transfer/import and only apply rollout:

```bash
SKIP_BUILD=true SKIP_IMAGE_TRANSFER=true ./playbook/deploy.sh
```

## Configure Sinks

`deploy.sh` prompts for sink selection when run interactively. Press Enter to keep the default sink set:

```text
postgres clickhouse qdrant redis
```

Non-interactive examples:

```bash
SINKS_ENABLED="postgres clickhouse" ./playbook/deploy.sh
SINKS_ENABLED="postgres,clickhouse,qdrant" ./playbook/deploy.sh
SINKS_ENABLED=none ./playbook/deploy.sh
ENABLE_SINK_PROMPT=false POSTGRES_ENABLED=true CLICKHOUSE_ENABLED=false QDRANT_ENABLED=false REDIS_ENABLED=false ./playbook/deploy.sh
```

The script passes these choices as Helm runtime overrides and patches the ConfigMap for raw kustomize deployments.

For raw Kubernetes deployment, sink enablement is controlled in:

```text
deploy/k8s/configmap.yaml
```

Common flags:

```yaml
POSTGRES_ENABLED: "true"
CLICKHOUSE_ENABLED: "true"
QDRANT_ENABLED: "true"
REDIS_ENABLED: "true"
STDOUT_ENABLED: "false"
```

Patch an existing deployment:

```bash
kubectl -n bosgenesis patch configmap bosgenesis-k8s-data-ingestion-agent-config \
  --type merge \
  -p '{"data":{"QDRANT_ENABLED":"false","REDIS_ENABLED":"false"}}'
kubectl -n bosgenesis rollout restart deployment/bosgenesis-k8s-data-ingestion-agent
```

For Helm deployment, override values:

```bash
helm upgrade --install bosgenesis-k8s-data-ingestion-agent \
  charts/bosgenesis-k8s-data-ingestion-agent \
  --namespace bosgenesis \
  --set config.qdrantEnabled=false \
  --set config.redisEnabled=false
```

Default PostgreSQL and ClickHouse sinks require credentials in the agent secret. For Helm deployments, use the credentials values example:

```bash
cp charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.example.yaml \
  charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml
```

Edit `values.credentials.yaml`, then deploy with `./playbook/deploy.sh`.

## Configure Scheduler

The default deployment runs in `service` mode, which starts both API and the hourly scheduler.

Scheduler settings:

```yaml
AGENT_SCAN_INTERVAL_SECONDS: "3600"
AGENT_RUN_ON_STARTUP: "true"
```

Disable scheduled scans and keep only on-demand API by changing the container args to:

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

Change the schedule to every 30 minutes:

```bash
kubectl -n bosgenesis patch configmap bosgenesis-k8s-data-ingestion-agent-config \
  --type merge \
  -p '{"data":{"AGENT_SCAN_INTERVAL_SECONDS":"1800"}}'
kubectl -n bosgenesis rollout restart deployment/bosgenesis-k8s-data-ingestion-agent
```

## Required Commands

Local machine:

- `docker`
- `kubectl`
- `ssh`
- `scp`

For Helm deployment:

- `helm`

Remote node:

- `sudo ctr`

## Uninstall

Uninstall raw Kubernetes resources:

```bash
chmod +x playbook/uninstaller.sh
./playbook/uninstaller.sh
```

Uninstall a Helm release:

```bash
./playbook/uninstaller.sh
```

Default values:

| Setting | Default |
|---|---|
| Namespace | `bosgenesis` |
| App name | `bosgenesis-k8s-data-ingestion-agent` |
| Helm release | `bosgenesis-k8s-data-ingestion-agent` |
| Deploy method | `helm` |
| Delete secret | `false` |
| Delete namespace | `false` |
| Delete remote image | `false` |
| Delete remote image tar | `false` |

By default, the uninstaller deletes only this agent's Deployment, Service, Ingress, ConfigMap, and ServiceAccount. It does not delete the optional secret because it can contain credentials, and it does not delete the `bosgenesis` namespace because that namespace is shared.

Delete the optional secret:

```bash
DELETE_SECRET=true ./playbook/uninstaller.sh
```

Remove the imported containerd image and copied tar from the remote node:

```bash
DELETE_REMOTE_IMAGE=true DELETE_REMOTE_TAR=true ./playbook/uninstaller.sh
```

Only delete the namespace if it is dedicated to this agent:

```bash
DELETE_NAMESPACE=true ./playbook/uninstaller.sh
```

## Verify Deployment

```bash
kubectl rollout status deployment/bosgenesis-k8s-data-ingestion-agent -n bosgenesis
kubectl get pod -n bosgenesis -o wide | grep bosgenesis-k8s-data-ingestion-agent
kubectl get svc bosgenesis-k8s-data-ingestion-agent -n bosgenesis
```

Port-forward the service:

```bash
kubectl -n bosgenesis port-forward svc/bosgenesis-k8s-data-ingestion-agent 8080:8080
```

Check health:

```bash
curl http://127.0.0.1:8080/health
```

Run an on-demand scan:

```bash
curl -X POST http://127.0.0.1:8080/scan/run \
  -H "Content-Type: application/json" \
  -d '{"trigger_type":"manual","namespace":"bosgenesis"}'
```
