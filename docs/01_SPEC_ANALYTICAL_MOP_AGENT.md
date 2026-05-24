# Analytical MoP Agent — Spec-Driven Development Specification

**Document status:** Draft v1.0  
**Target platform:** BOS Genesis / BOS AI Studio  
**Agent name:** `analytical-mop-agent`  
**Primary mode:** Periodic namespace scanner and analytical ETL agent  
**Secondary mode:** On-demand callable agent/tool for LLMs and other agents  
**Initial namespace:** `bosgenesis`  
**Execution posture:** Read-only collection, persistence, trace, and stream/print fallback  

---

## 1. Purpose

The Analytical MoP Agent is a long-running ETL-style agent that periodically scans a configured Kubernetes namespace using existing BOS Genesis tools and MCP servers. It collects Kubernetes and Helm operational state, detects whether the collected state has changed, and persists only new or changed snapshots into configured analytical stores.

The agent does **not** perform anomaly detection, alerting, remediation, MoP execution, Helm mutation, Kubernetes mutation, or autonomous action. Its role is to create a clean operational data foundation for later machine learning, anomaly detection, analytics, and future MoP-generation agents.

---

## 2. Business Motivation

BOS Genesis already has operational components such as Kubernetes MCP, Helm MCP, PostgreSQL, ClickHouse, Qdrant, Redis, Langfuse, SigNoz, Kafka, LangGraph/LangMem-style memory, and other observability components. The Analytical MoP Agent connects these components into a consistent data collection layer.

This enables future use cases such as:

- Kubernetes namespace health trend analysis.
- Helm release drift analysis.
- Deployment lifecycle history.
- Resource change timeline.
- MoP readiness scoring.
- Later anomaly detection using PostgreSQL/pgvector/ClickHouse/Qdrant.
- Agentic troubleshooting memory.
- Evidence collection for MoP generation.

---

## 3. Scope

### 3.1 In Scope

- Periodically scan the configured namespace.
- Collect data using Kubernetes Inspector MCP read tools.
- Collect data using Helm Manager MCP read tools.
- Normalize Kubernetes and Helm state into a canonical observation model.
- Compute content hash/change fingerprint per resource/release snapshot.
- Insert new/changed data into PostgreSQL when enabled.
- Insert analytical facts/events into ClickHouse when enabled.
- Optionally write semantic memory/index records into Qdrant/pgvector when enabled.
- Optionally cache latest snapshot/deduplication state in Redis when enabled.
- Trace every agent run and major operation using Langfuse when enabled.
- Emit OpenTelemetry traces to SigNoz when enabled.
- Expose an on-demand API endpoint and/or MCP-callable tool surface.
- Stream collected data to caller or print to stdout if all persistence components are disabled.
- Include Letta adapter skeleton but keep it disabled by configuration.

### 3.2 Out of Scope

- Anomaly detection.
- Alerting.
- MoP execution.
- Kubernetes mutation.
- Helm mutation.
- Automated remediation.
- Production change approval.
- Direct `kubectl` or `helm` shell execution from this agent.
- Secret collection.
- RBAC mutation.
- Cross-namespace inspection unless explicitly configured later.

---

## 4. Existing Tool Dependencies

### 4.1 Kubernetes Inspector MCP

The agent uses the existing namespace-scoped Kubernetes Inspector MCP server.

Default endpoint:

```text
http://k8s-inspector.bosgenesis.local/mcp
```

Read tools expected:

- `k8s_namespace_summary`
- `k8s_list_pods`
- `k8s_describe_pod`
- `k8s_get_pod_logs`
- `k8s_list_services`
- `k8s_list_pvcs`
- `k8s_describe_pvc`
- `k8s_list_deployments`
- `k8s_list_statefulsets`
- `k8s_list_ingresses`
- `k8s_list_events`

### 4.2 Helm Manager MCP

The agent uses the existing Helm MCP server.

Default endpoint:

```text
http://helm-manager.bosgenesis.local/mcp
```

Read tools expected:

- `helm_list_releases`
- `helm_release_status`
- `helm_release_history`
- `helm_get_values`
- `helm_get_manifest`
- `helm_show_chart`
- `helm_template_chart`
- `helm_repo_list`

---

## 5. User Stories

### US-1 — Periodic namespace scan

As a platform engineer, I want the agent to scan the `bosgenesis` namespace periodically so that operational state is captured without manual effort.

**Acceptance criteria:**

- Agent starts as a long-running service.
- Scan interval is configurable.
- Each scan has a unique `run_id` and `correlation_id`.
- Each scan uses MCP read tools only.
- Each scan is traced when tracing is enabled.

### US-2 — Store changed data in PostgreSQL

As a data engineer, I want only changed snapshots stored in PostgreSQL so that I can train future ML models without unnecessary duplication.

**Acceptance criteria:**

- PostgreSQL can be enabled/disabled by config.
- Data model supports scan runs, resource snapshots, Helm release snapshots, and change events.
- If a resource hash is unchanged, the agent does not insert a duplicate snapshot unless full history mode is enabled.

### US-3 — Store analytics data in ClickHouse

As an analytics engineer, I want lightweight facts/events in ClickHouse so dashboards can show trends and operational patterns.

**Acceptance criteria:**

- ClickHouse can be enabled/disabled by config.
- Run summaries and resource facts are inserted into ClickHouse when enabled.
- Failed ClickHouse insert does not crash the whole agent unless strict mode is enabled.

### US-4 — Trace every operation

As an SRE, I want every scan and MCP call traced so that I can debug the collector itself.

**Acceptance criteria:**

- Langfuse tracing can be enabled/disabled.
- SigNoz/OpenTelemetry can be enabled/disabled.
- Each MCP call has a span.
- Each persistence operation has a span.
- Each run includes status, latency, counts, and errors.

### US-5 — On-demand invocation

As another agent or LLM, I want to call the Analytical MoP Agent on demand to get a fresh namespace snapshot.

**Acceptance criteria:**

- Exposes `POST /scan/run` for immediate scan.
- Optional MCP tool `analytical_mop_scan_namespace` is available.
- Response can stream/return data if no persistence is enabled.

### US-6 — Memory integration

As a future MoP/troubleshooting agent, I want this agent to write useful operational observations into BOS Genesis memory stores.

**Acceptance criteria:**

- Qdrant memory sink is configurable.
- pgvector memory sink is configurable.
- Redis latest-state cache is configurable.
- LangMem-compatible extraction hook exists.
- Letta adapter exists but is disabled by default.

---

## 6. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | Agent shall run as a long-running service. |
| FR-2 | Agent shall support periodic scheduled scan. |
| FR-3 | Agent shall support on-demand scan through REST API. |
| FR-4 | Agent shall optionally expose MCP tool surface for other agents. |
| FR-5 | Agent shall call K8s MCP read tools only. |
| FR-6 | Agent shall call Helm MCP read tools only. |
| FR-7 | Agent shall normalize all collected data into canonical observation records. |
| FR-8 | Agent shall compute stable content hashes for deduplication/change detection. |
| FR-9 | Agent shall persist changed snapshots into PostgreSQL when enabled. |
| FR-10 | Agent shall persist analytical event/fact rows into ClickHouse when enabled. |
| FR-11 | Agent shall write semantic memory records into Qdrant when enabled. |
| FR-12 | Agent shall write vector memory into pgvector when enabled. |
| FR-13 | Agent shall cache latest resource hash/state in Redis when enabled. |
| FR-14 | Agent shall emit Langfuse traces when enabled. |
| FR-15 | Agent shall emit OpenTelemetry traces for SigNoz when enabled. |
| FR-16 | Agent shall stream or print results if all persistence sinks are disabled. |
| FR-17 | Agent shall not perform anomaly detection or alerting. |
| FR-18 | Agent shall not mutate Kubernetes or Helm state. |
| FR-19 | Agent shall keep Letta adapter disabled by default. |
| FR-20 | Agent shall maintain structured run summaries. |

---

## 7. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | Configuration-driven; all external dependencies must be optional. |
| NFR-2 | Fail-soft mode by default for optional sinks. |
| NFR-3 | Strict mode available to fail run when mandatory sink fails. |
| NFR-4 | Idempotent periodic scans. |
| NFR-5 | No secrets collected or persisted. |
| NFR-6 | Structured JSON logs. |
| NFR-7 | Suitable for Kubernetes deployment in `bosgenesis`. |
| NFR-8 | Supports local development mode. |
| NFR-9 | Modular sink architecture. |
| NFR-10 | Agent should be safe to run frequently without database explosion. |

---

## 8. Configuration Specification

Environment variables should override YAML configuration.

```yaml
agent:
  name: analytical-mop-agent
  namespace: bosgenesis
  scan_interval_seconds: 300
  run_on_startup: true
  strict_mode: false
  full_history_mode: false

mcp:
  k8s_inspector:
    enabled: true
    endpoint: http://k8s-inspector.bosgenesis.local/mcp
    timeout_seconds: 30
  helm_manager:
    enabled: true
    endpoint: http://helm-manager.bosgenesis.local/mcp
    timeout_seconds: 30

sinks:
  postgres:
    enabled: true
    dsn: postgresql://user:password@postgresql.bosgenesis.svc.cluster.local:5432/bosgenesis
    use_pgvector: false
  clickhouse:
    enabled: true
    host: clickhouse.bosgenesis.svc.cluster.local
    port: 8123
    database: bosgenesis
  qdrant:
    enabled: false
    url: http://qdrant.bosgenesis.svc.cluster.local:6333
    collection: analytical_mop_observations
  redis:
    enabled: false
    url: redis://redis.bosgenesis.svc.cluster.local:6379/0
  langmem:
    enabled: false
  letta:
    enabled: false
    url: http://letta.bosgenesis.local

observability:
  langfuse:
    enabled: true
    host: http://langfuse.bosgenesis.local
  signoz:
    enabled: true
    otlp_endpoint: http://signoz-otel-collector.signoz:4317
  kafka_events:
    enabled: false
    bootstrap_servers: kafka.bosgenesis.svc.cluster.local:9092
    topic: analytical-mop-agent-events

api:
  enabled: true
  host: 0.0.0.0
  port: 8080
  api_key_required: true
```

---

## 9. Canonical Observation Model

### 9.1 Scan Run

```json
{
  "run_id": "uuid",
  "correlation_id": "uuid",
  "agent_name": "analytical-mop-agent",
  "namespace": "bosgenesis",
  "trigger_type": "scheduled|on_demand|mcp",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "status": "success|partial_success|failed",
  "resources_seen": 0,
  "resources_changed": 0,
  "helm_releases_seen": 0,
  "helm_releases_changed": 0,
  "error_count": 0
}
```

### 9.2 Resource Snapshot

```json
{
  "snapshot_id": "uuid",
  "run_id": "uuid",
  "namespace": "bosgenesis",
  "source": "k8s_mcp",
  "resource_type": "pod|deployment|service|ingress|pvc|event|statefulset",
  "resource_name": "string",
  "resource_uid": "string|null",
  "observed_at": "timestamp",
  "status_summary": "string",
  "content_hash": "sha256",
  "raw_payload": {},
  "normalized_payload": {}
}
```

### 9.3 Helm Release Snapshot

```json
{
  "snapshot_id": "uuid",
  "run_id": "uuid",
  "namespace": "bosgenesis",
  "source": "helm_mcp",
  "release_name": "string",
  "revision": 1,
  "chart": "string",
  "app_version": "string|null",
  "status": "deployed|failed|pending|unknown",
  "observed_at": "timestamp",
  "content_hash": "sha256",
  "values_hash": "sha256|null",
  "manifest_hash": "sha256|null",
  "raw_payload": {},
  "normalized_payload": {}
}
```

---

## 10. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| AC-1 | Agent starts with only K8s MCP enabled and no database enabled. |
| AC-2 | Agent prints/streams collected data when all sinks are disabled. |
| AC-3 | Agent successfully scans namespace using K8s MCP. |
| AC-4 | Agent successfully scans Helm releases using Helm MCP. |
| AC-5 | Agent inserts scan run into PostgreSQL when enabled. |
| AC-6 | Agent inserts resource snapshots only when hash changes. |
| AC-7 | Agent inserts analytical facts into ClickHouse when enabled. |
| AC-8 | Agent emits Langfuse trace when enabled. |
| AC-9 | Agent emits OpenTelemetry spans visible in SigNoz when enabled. |
| AC-10 | Agent exposes `POST /scan/run`. |
| AC-11 | Agent exposes `GET /health`. |
| AC-12 | Agent returns partial success when optional sink fails in non-strict mode. |
| AC-13 | Agent never calls mutation tools. |
| AC-14 | Agent has Letta adapter class/module but disabled by default. |

---

## 11. Suggested Project Structure

```text
analytical-mop-agent/
  README.md
  pyproject.toml
  Dockerfile
  .env.example

  src/analytical_mop_agent/
    main.py
    config.py
    api.py
    scheduler.py
    models.py
    orchestrator.py

    mcp_clients/
      base.py
      k8s_inspector_client.py
      helm_manager_client.py

    collectors/
      namespace_collector.py
      helm_collector.py
      log_collector.py
      event_collector.py

    normalize/
      k8s_normalizer.py
      helm_normalizer.py
      hashing.py

    sinks/
      base.py
      postgres_sink.py
      clickhouse_sink.py
      qdrant_sink.py
      redis_sink.py
      pgvector_sink.py
      langmem_sink.py
      letta_sink_disabled.py
      stdout_sink.py

    observability/
      trace_context.py
      langfuse_tracer.py
      otel_tracer.py
      structured_logger.py

    memory/
      memory_router.py
      memory_record_builder.py

    tests/
      test_hashing.py
      test_config.py
      test_normalizers.py
      test_stdout_fallback.py
      test_no_mutation_tools.py

  k8s/
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
    secret.yaml
    cronjob-optional.yaml
```

---

## 12. Mermaid — Spec View

```mermaid
flowchart LR
    Trigger[Scheduled / On-demand / MCP call] --> Agent[Analytical MoP Agent]

    Agent --> K8S[K8s Inspector MCP Read Tools]
    Agent --> HELM[Helm Manager MCP Read Tools]

    K8S --> Normalize[Normalize + Hash]
    HELM --> Normalize

    Normalize --> Changed{Changed?}
    Changed -->|No| Skip[Skip Duplicate Snapshot]
    Changed -->|Yes| Persist[Persist Snapshot]

    Persist --> PG[(PostgreSQL)]
    Persist --> CH[(ClickHouse)]
    Persist --> QD[(Qdrant / pgvector Optional)]
    Persist --> REDIS[(Redis Latest State Optional)]

    Agent --> LF[Langfuse Trace]
    Agent --> SZ[SigNoz / OTel Trace]

    Skip --> Summary[Run Summary]
    Persist --> Summary
    Summary --> Caller[Return / Stream / Print]
```

---

## 13. Definition of Done

The agent is considered done when:

- It can run continuously in Kubernetes.
- It can scan namespace and Helm state periodically.
- It can be triggered on-demand.
- It persists only changed observations when PostgreSQL is enabled.
- It writes analytical facts when ClickHouse is enabled.
- It traces each run through Langfuse and SigNoz when enabled.
- It does not mutate cluster or Helm state.
- It degrades gracefully to stdout/streaming mode when all optional dependencies are disabled.
