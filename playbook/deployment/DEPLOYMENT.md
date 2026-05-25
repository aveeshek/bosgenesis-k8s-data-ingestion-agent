# Deployment Guide

## Build and Deploy Through Containerd Import

Default deployment target:

- Namespace: `bosgenesis`
- Deployment: `bosgenesis-k8s-data-ingestion-agent`
- Container: `app`
- Image: `bosgenesis-k8s-data-ingestion-agent:0.0.1`
- Remote node: `taieuser@10.99.52.165`

Run:

```bash
chmod +x playbook/deploy.sh
./playbook/deploy.sh
```

Equivalent explicit command:

```bash
IMAGE_TAG=0.0.1 \
REMOTE_USER=taieuser \
REMOTE_HOST=10.99.52.165 \
./playbook/deploy.sh
```

## Ingress

```bash
./playbook/deploy.sh
```

Ingress is enabled by default.

Default ingress host:

```text
data-ingestion-agent.bosgenesis.local
```

Disable ingress:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

## Helm Deployment

```bash
./playbook/deploy.sh
```

For PostgreSQL and ClickHouse credentials, create a private Helm values file:

```bash
cp charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.example.yaml \
  charts/bosgenesis-k8s-data-ingestion-agent/values.credentials.yaml
```

Edit `values.credentials.yaml`, then deploy:

```bash
./playbook/deploy.sh
```

Deploy with Helm and default ingress:

```bash
./playbook/deploy.sh
```

Disable ingress with Helm:

```bash
ENABLE_INGRESS=false ./playbook/deploy.sh
```

## Runtime Modes

The default deployment runs:

```bash
bosgenesis-k8s-data-ingestion-agent service
```

This starts both:

- REST API for on-demand scans.
- Scheduler for hourly scans.

To run API only or scheduler only, change deployment args:

```yaml
args: ["api"]
```

or:

```yaml
args: ["scheduler"]
```

## Verify

```bash
kubectl rollout status deployment/bosgenesis-k8s-data-ingestion-agent -n bosgenesis
kubectl get pod -n bosgenesis -o wide | grep bosgenesis-k8s-data-ingestion-agent
kubectl get svc bosgenesis-k8s-data-ingestion-agent -n bosgenesis
```

Port-forward:

```bash
kubectl -n bosgenesis port-forward svc/bosgenesis-k8s-data-ingestion-agent 8080:8080
curl http://127.0.0.1:8080/health
```

On-demand scan:

```bash
curl -X POST http://127.0.0.1:8080/scan/run \
  -H "Content-Type: application/json" \
  -d '{"trigger_type":"manual","namespace":"bosgenesis"}'
```
