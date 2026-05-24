# Analytical MoP Agent — High Level Design

**Document status:** Draft v1.0  
**Target platform:** BOS Genesis / BOS AI Studio  
**Agent name:** `analytical-mop-agent`  

---

## 1. Executive Summary

The Analytical MoP Agent is a read-only, periodic, ETL-style agent for Kubernetes operational state collection. It uses the existing BOS Genesis Kubernetes Inspector MCP and Helm Manager MCP servers to scan a namespace, collect resource and Helm release data, normalize the collected data, detect changes through hashing, and persist the resulting facts into PostgreSQL and ClickHouse when enabled.

It is not a remediation agent. It does not perform anomaly detection or alerts. It creates the analytical and machine-learning-ready data layer required by future MoP generation, anomaly detection, SRE analytics, and decision-support agents.

---

## 2. High-Level Architecture

```mermaid
flowchart LR
    subgraph Entry[Invocation Layer]
        Scheduler[Periodic Scheduler]
        REST[REST API /scan/run]
        MCPTool[Optional MCP Tool]
        LLM[LLM / Other Agent]
    end

    subgraph Agent[Analytical MoP Agent]
        Gateway[Request Gateway]
        Orchestrator[Scan Orchestrator]
        KCollector[Kubernetes Collector]
        HCollector[Helm Collector]
        Normalizer[Normalizer + Hash Engine]
        ChangeDetector[Change Detector]
        SinkRouter[Sink Router]
    end

    subgraph ExistingMCP[Existing MCP Servers]
        K8SMCP[K8s Inspector MCP]
        HELMMCP[Helm Manager MCP]
    end

    subgraph Stores[Optional Data Stores]
        PG[(PostgreSQL / pgvector)]
        CH[(ClickHouse)]
        QD[(Qdrant)]
        REDIS[(Redis)]
        OUT[Stdout / Streaming]
    end

    subgraph Observability[Optional Observability]
        LF[Langfuse]
        SZ[SigNoz / OpenTelemetry]
        LOG[Structured Logs]
    end

    Scheduler --> Gateway
    REST --> Gateway
    MCPTool --> Gateway
    LLM --> REST

    Gateway --> Orchestrator
    Orchestrator --> KCollector
    Orchestrator --> HCollector

    KCollector --> K8SMCP
    HCollector --> HELMMCP

    KCollector --> Normalizer
    HCollector --> Normalizer
    Normalizer --> ChangeDetector
    ChangeDetector --> SinkRouter

    SinkRouter --> PG
    SinkRouter --> CH
    SinkRouter --> QD
    SinkRouter --> REDIS
    SinkRouter --> OUT

    Orchestrator --> LF
    Orchestrator --> SZ
    Orchestrator --> LOG
```

---

## 3. Major Capabilities

| Capability | Description |
|---|---|
| Periodic scan | Runs on a configurable interval. |
| On-demand scan | Callable through REST/API/MCP. |
| Kubernetes collection | Uses K8s MCP read tools for pods, deployments, services, PVCs, ingresses, events, logs. |
| Helm collection | Uses Helm MCP read tools for releases, status, values, manifests, history. |
| Change detection | Uses stable hashes to persist only changed data. |
| PostgreSQL persistence | Stores normalized scan runs and resource snapshots for ML. |
| ClickHouse persistence | Stores analytical facts and event-style data for dashboards. |
| Memory integration | Optional Qdrant, pgvector, Redis, LangMem-style memory hooks. |
| Observability | Optional Langfuse traces and SigNoz OTel spans. |
| Fallback mode | Streams/prints result if all sinks are disabled. |

---

## 4. Deployment Context

```mermaid
flowchart TB
    subgraph Cluster[Kubernetes Cluster]
        subgraph BOS[Namespace: bosgenesis]
            AgentPod[Deployment: analytical-mop-agent]
            AgentSvc[Service: analytical-mop-agent]
            AgentIng[Optional Ingress]

            K8SINS[K8s Inspector MCP]
            HELMMGR[Helm Manager MCP]

            PG[(PostgreSQL)]
            CH[(ClickHouse)]
            QD[(Qdrant)]
            REDIS[(Redis)]
            LF[Langfuse]
        end

        subgraph SIGNOZ[Namespace: signoz]
            Collector[SigNoz OTel Collector]
            SigUI[SigNoz UI]
        end
    end

    AgentIng --> AgentSvc
    AgentSvc --> AgentPod
    AgentPod --> K8SINS
    AgentPod --> HELMMGR
    AgentPod --> PG
    AgentPod --> CH
    AgentPod --> QD
    AgentPod --> REDIS
    AgentPod --> LF
    AgentPod --> Collector
```

---

## 5. Component Responsibilities

### 5.1 Request Gateway

Receives scan requests from scheduler, REST API, optional MCP tool, or LLM-triggered caller. It creates `run_id`, `correlation_id`, and run context.

### 5.2 Scan Orchestrator

Coordinates the full run lifecycle:

1. Start trace.
2. Collect Kubernetes facts.
3. Collect Helm facts.
4. Normalize data.
5. Detect changes.
6. Persist or stream output.
7. Write run summary.
8. Close trace.

### 5.3 Kubernetes Collector

Calls Kubernetes Inspector MCP read tools only. It never calls write or mutation tools.

### 5.4 Helm Collector

Calls Helm Manager MCP read tools only. It never calls install, upgrade, uninstall, or rollback tools.

### 5.5 Normalizer + Hash Engine

Transforms raw MCP responses into canonical records. Removes volatile fields where needed and computes stable hashes.

### 5.6 Change Detector

Compares current hash against latest known hash from PostgreSQL or Redis. If no persistence is available, it treats all records as output records.

### 5.7 Sink Router

Routes records to configured sinks:

- PostgreSQL sink.
- ClickHouse sink.
- Qdrant sink.
- pgvector sink.
- Redis cache sink.
- LangMem sink.
- disabled Letta adapter.
- stdout/streaming fallback.

### 5.8 Observability Layer

Emits:

- Langfuse trace per run.
- OpenTelemetry spans per run, collector, MCP call, normalization, and sink operation.
- Structured logs.

---

## 6. Data Flow

```mermaid
sequenceDiagram
    participant S as Scheduler/API/LLM
    participant A as Analytical MoP Agent
    participant K as K8s MCP
    participant H as Helm MCP
    participant N as Normalizer
    participant D as Change Detector
    participant P as PostgreSQL
    participant C as ClickHouse
    participant O as Observability

    S->>A: Trigger scan
    A->>O: Start run trace
    A->>K: Read namespace summary/resources/events/logs
    K-->>A: Kubernetes state
    A->>H: Read releases/status/history/values/manifests
    H-->>A: Helm state
    A->>N: Normalize raw data
    N-->>A: Canonical observations
    A->>D: Compute and compare hashes
    D-->>A: New/changed records
    A->>P: Insert run + changed snapshots if enabled
    A->>C: Insert analytical facts if enabled
    A->>O: Close trace with summary
    A-->>S: Return run summary and optional stream
```

---

## 7. Read-Only Tool Policy

The Analytical MoP Agent must only use read tools from both MCP servers.

```mermaid
flowchart TB
    Agent[Analytical MoP Agent] --> ToolSelect{Tool Type?}

    ToolSelect -->|K8s Read| AllowK[Allow]
    ToolSelect -->|Helm Read| AllowH[Allow]
    ToolSelect -->|K8s Mutation| DenyK[Deny in code]
    ToolSelect -->|Helm Mutation| DenyH[Deny in code]

    AllowK --> Execute[Execute Read Tool]
    AllowH --> Execute
    DenyK --> AuditDeny[Log/Trace blocked attempt]
    DenyH --> AuditDeny
```

---

## 8. Storage Strategy

### 8.1 PostgreSQL

PostgreSQL is the source of truth for normalized scan runs and changed snapshots. It is suitable for later supervised ML feature engineering and exact historical queries.

### 8.2 ClickHouse

ClickHouse stores event/fact tables optimized for trend analysis, dashboarding, and later anomaly detection. It should receive compact analytical rows rather than very large raw payloads.

### 8.3 Qdrant / pgvector

Qdrant and pgvector are optional semantic memory stores. They can store compact textual summaries of operational observations such as:

- "deployment memory-agent had 3 ready replicas and no restarts"
- "helm release langflow revision changed from 3 to 4"
- "pod status changed from Pending to Running"

### 8.4 Redis

Redis can cache latest hashes and latest namespace summary to avoid repeated database reads.

### 8.5 Letta

Letta adapter remains present but disabled. It should not be initialized unless explicitly enabled in future.

---

## 9. Observability Design

```mermaid
flowchart LR
    Agent[Analytical MoP Agent] --> TraceCtx[Trace Context]

    TraceCtx --> LF[Langfuse Run Trace]
    TraceCtx --> OTEL[OpenTelemetry Spans]
    TraceCtx --> Logs[Structured JSON Logs]

    OTEL --> SZ[SigNoz Collector]
    Logs --> STDOUT[Container Logs]
```

Recommended span names:

```text
analytical_mop.scan.start
analytical_mop.k8s.collect
analytical_mop.helm.collect
analytical_mop.normalize
analytical_mop.change_detect
analytical_mop.sink.postgres
analytical_mop.sink.clickhouse
analytical_mop.sink.qdrant
analytical_mop.sink.redis
analytical_mop.scan.complete
```

---

## 10. Failure Handling

| Failure | Default Behavior |
|---|---|
| K8s MCP unavailable | Mark partial failure; continue Helm if enabled. |
| Helm MCP unavailable | Mark partial failure; continue K8s if enabled. |
| PostgreSQL unavailable | Skip sink in non-strict mode; trace error. |
| ClickHouse unavailable | Skip sink in non-strict mode; trace error. |
| Langfuse unavailable | Continue; log tracing failure. |
| SigNoz unavailable | Continue; log OTel export failure. |
| All sinks disabled | Stream/print result to caller/stdout. |

---

## 11. HLD Mermaid — Run Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> ScheduledRun: interval reached
    Idle --> OnDemandRun: API/MCP/LLM call

    ScheduledRun --> InitializeRun
    OnDemandRun --> InitializeRun

    InitializeRun --> CollectK8s
    InitializeRun --> CollectHelm

    CollectK8s --> Normalize
    CollectHelm --> Normalize

    Normalize --> DetectChanges
    DetectChanges --> PersistEnabled: sinks enabled
    DetectChanges --> StreamOnly: no sinks enabled

    PersistEnabled --> WritePostgres
    PersistEnabled --> WriteClickHouse
    PersistEnabled --> WriteMemoryStores

    WritePostgres --> CompleteRun
    WriteClickHouse --> CompleteRun
    WriteMemoryStores --> CompleteRun
    StreamOnly --> CompleteRun

    CompleteRun --> Idle
```

---

## 12. HLD Decision Summary

| Decision | Choice |
|---|---|
| Runtime style | Long-running service with scheduler + API. |
| Agent behavior | Read-only ETL scanner. |
| Tool access | Existing K8s MCP and Helm MCP read tools only. |
| Persistence | Optional PostgreSQL and ClickHouse first. |
| Memory | Optional Qdrant, pgvector, Redis, LangMem. |
| Letta | Adapter available but disabled. |
| Observability | Langfuse + SigNoz optional and configurable. |
| Fallback | Stream/print if all sinks disabled. |
