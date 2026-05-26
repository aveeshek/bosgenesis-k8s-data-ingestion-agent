# BOS Genesis K8s Data Ingestion Agent - High Level Design

**Document status:** Implemented baseline  
**Service:** `bosgenesis-k8s-data-ingestion-agent`  
**Namespace:** `bosgenesis`

---

## 1. Executive Summary

The agent is a read-only operational data collector for BOS Genesis. It exposes REST and remote MCP interfaces, uses existing Kubernetes and Helm MCP servers as controlled read boundaries, persists changed observations to optional sinks, and emits Langfuse traces for each scan.

The design favors explicit deterministic code over LLM orchestration frameworks. MCP is the tool boundary; Langfuse is the tracing plane; sinks are independently configurable.

---

## 2. System Context

```mermaid
flowchart TB
    subgraph Users["External callers"]
        Codex["Codex"]
        GPT["GPT-5 / agent"]
        Human["Operator"]
        Langflow["Langflow read-only flow"]
    end

    subgraph BOS["Kubernetes namespace: bosgenesis"]
        Agent["bosgenesis-k8s-data-ingestion-agent"]
        K8S["bosgenesis-k8s-inspector-mcp"]
        Helm["bosgenesis-helm-manager-mcp"]
        PG[("Postgres")]
        CH[("ClickHouse")]
        QD[("Qdrant")]
        RD[("Redis")]
        LF["Langfuse web + worker"]
    end

    Codex -->|"Remote MCP /mcp"| Agent
    GPT -->|"Remote MCP /mcp"| Agent
    Human -->|"REST"| Agent
    Langflow -->|"GET /health or /scan/latest"| Agent

    Agent -->|"read tools"| K8S
    Agent -->|"read tools"| Helm
    Agent --> PG
    Agent --> CH
    Agent --> QD
    Agent --> RD
    Agent -->|"OTLP/Langfuse SDK"| LF
```

---

## 3. Major Runtime Interfaces

| Interface | URL / Path | Purpose |
|---|---|---|
| REST health | `/health` | Health and safe effective config. |
| REST run scan | `/scan/run` | Trigger one scan. |
| REST latest scan | `/scan/latest` | Return latest in-memory summary. |
| REST config | `/config/effective` | Return redacted effective config. |
| Remote MCP | `/mcp` | MCP tool surface for Codex/agents. |
| Langflow status flow | `langflow/data-ingestion-agent-status-flow.json` | Read-only status flow. |

---

## 4. Internal Components

```mermaid
flowchart LR
    API["FastAPI app"] --> Orchestrator["Scan orchestrator"]
    MCPServer["MCP server mounted at /mcp"] --> Orchestrator
    Scheduler["Scheduler/service loop"] --> Orchestrator

    Orchestrator --> KCollector["K8s collector"]
    Orchestrator --> HCollector["Helm collector"]
    KCollector --> KClient["K8s MCP client"]
    HCollector --> HClient["Helm MCP client"]

    Orchestrator --> Normalizers["K8s + Helm normalizers"]
    Normalizers --> Hasher["Stable hash engine"]
    Hasher --> Detector["Change detector"]
    Detector --> SinkRouter["Sink router"]

    SinkRouter --> Sinks["Postgres / ClickHouse / Qdrant / Redis / stdout"]
    Orchestrator --> Tracer["Langfuse tracer"]
    Orchestrator --> Logger["Structured logger"]
```

---

## 5. Deployment Context

```mermaid
flowchart TB
    Ingress["Ingress: data-ingestion-agent.bosgenesis.local"] --> Service["Service: bosgenesis-k8s-data-ingestion-agent"]
    Service --> Pod["Deployment pod: app container"]

    Pod --> ConfigMap["ConfigMap: non-secret settings"]
    Pod --> Secret["Secret: credentials"]
    Pod --> K8SService["K8s Inspector MCP service DNS"]
    Pod --> HelmService["Helm Manager MCP service DNS"]
    Pod --> LangfuseService["langfuse-web.bosgenesis.svc.cluster.local:3000"]
```

Runtime URLs inside the pod use service DNS, not external ingress names, for MCP dependencies and Langfuse.

---

## 6. Observability Flow

```mermaid
sequenceDiagram
    participant C as Codex/Agent
    participant A as Data Ingestion Agent
    participant K as K8s MCP
    participant H as Helm MCP
    participant L as Langfuse

    C->>A: data_ingestion_run_scan
    A->>L: start trace data-ingestion.scan
    A->>K: read namespace resources
    K-->>A: resource payloads
    A->>H: read Helm data
    H-->>A: release payloads
    A->>A: normalize/hash/detect changes
    A->>A: write enabled sinks
    A->>L: close trace with summary
    A-->>C: run summary with trace_ids.langfuse
```

Langfuse root trace:

```text
data-ingestion.scan
```

Implemented child spans:

```text
collect.kubernetes
collect.helm
normalize
hash
detect_changes
write_sinks
write_memory
```

---

## 7. Safety Design

| Safety rule | Design choice |
|---|---|
| No direct Kubernetes access | Agent calls K8s MCP instead of Kubernetes API. |
| No direct Helm mutation | Agent calls Helm MCP read operations only. |
| No secret collection | Collectors avoid Kubernetes Secrets. |
| No raw shell tooling | No `kubectl` or `helm` shell execution path. |
| No LLM planner | Deterministic orchestrator avoids unreviewed autonomous behavior. |
| Redacted health/config | Secret settings are redacted from safe config output. |

---

## 8. Runtime Decisions

| Decision | Current implementation |
|---|---|
| API framework | FastAPI |
| MCP transport | Streamable HTTP mounted at `/mcp` |
| Langfuse | Enabled by default, disableable by config |
| Langfuse URL | `http://langfuse-web.bosgenesis.svc.cluster.local:3000` |
| Sink defaults | Postgres, ClickHouse, Qdrant, Redis enabled |
| Deploy sink override | `playbook/deploy.sh` prompt/env overrides |
| LangChain | Not used; not needed for deterministic ETL |
| Langflow | Importable visualization and read-only status flow |
