# BOS Genesis K8s Data Ingestion Agent - Low Level Design

**Document status:** Implemented baseline  
**Package:** `bosgenesis_k8s_data_ingestion_agent`

---

## 1. Module Map

```mermaid
flowchart TB
    App["api/app.py"] --> McpApi["api/mcp.py"]
    App --> Main["entrypoints/main.py"]
    Runtime["entrypoints/runtime.py"] --> Main

    Main --> Config["config/__init__.py"]
    Main --> Orchestrator["core/orchestrator.py"]
    Main --> Logging["observability/logging.py"]
    Main --> Langfuse["observability/langfuse.py"]

    Orchestrator --> K8sCollector["collectors/k8s.py"]
    Orchestrator --> HelmCollector["collectors/helm.py"]
    K8sCollector --> K8sClient["mcp_clients/k8s.py"]
    HelmCollector --> HelmClient["mcp_clients/helm.py"]
    K8sClient --> BaseClient["mcp_clients/base.py"]
    HelmClient --> BaseClient

    Orchestrator --> Normalizer["normalizers/pipeline.py"]
    Normalizer --> K8sNorm["normalizers/k8s.py"]
    Normalizer --> HelmNorm["normalizers/helm.py"]
    Normalizer --> Hash["hashing/stable.py"]
    Orchestrator --> ChangeDetector["change_detection/detector.py"]

    Orchestrator --> SinkRouter["sinks/router.py"]
    SinkRouter --> PG["sinks/postgres"]
    SinkRouter --> CH["sinks/clickhouse"]
    SinkRouter --> QD["sinks/qdrant"]
    SinkRouter --> RD["sinks/redis"]
    SinkRouter --> STDOUT["sinks/stdout.py"]

    Orchestrator --> MemoryRouter["memory/router.py"]
    MemoryRouter --> MemoryRecords["memory/record_builder.py"]
```

---

## 2. Entry Points

### 2.1 REST API

| Endpoint | Method | Function |
|---|---:|---|
| `/health` | GET | Returns service health and safe effective config. |
| `/scan/run` | POST | Runs an on-demand scan. |
| `/scan/latest` | GET | Returns latest in-memory scan summary. |
| `/config/effective` | GET | Returns redacted config. |

### 2.2 MCP API

Mounted at:

```text
/mcp
```

Tools:

| MCP tool | Purpose |
|---|---|
| `data_ingestion_health` | Health and safe config. |
| `data_ingestion_run_scan` | On-demand scan. |
| `data_ingestion_latest_scan` | Latest summary. |
| `data_ingestion_effective_config` | Redacted config. |

```mermaid
flowchart LR
    Codex["Codex MCP client"] --> HTTP["POST /mcp"]
    HTTP --> Tools["MCP tools"]
    Tools --> Orchestrator["Scan orchestrator"]
    Orchestrator --> Summary["ScanSummary"]
    Summary --> Codex
```

---

## 3. Configuration Model

Settings are loaded from defaults and environment variables. Secret values are redacted in safe output.

```mermaid
flowchart LR
    Defaults["Code defaults"] --> Env["Environment variables"]
    Env --> Settings["Settings object"]
    Settings --> Safe["effective_safe_dict()"]
    Safe --> Health["/health and /config/effective"]
```

Key groups:

- Agent settings: namespace, startup run, interval, strict sink behavior.
- API settings: host, port, MCP allowed hosts.
- MCP settings: K8s/Helm URLs, host headers, timeouts.
- Sink settings: Postgres, ClickHouse, Qdrant, Redis, stdout.
- Observability settings: Langfuse and optional future SigNoz.

---

## 4. MCP Client Design

The base MCP client handles Streamable HTTP sessions, protocol initialization, tool calls, timeout handling, and host headers.

```mermaid
sequenceDiagram
    participant Collector
    participant Client as MCP client
    participant Server as Remote MCP server

    Collector->>Client: call_tool(name,args)
    Client->>Server: initialize
    Server-->>Client: session id
    Client->>Server: tools/call
    Server-->>Client: tool result
    Client-->>Collector: parsed payload
```

Read-only policy is enforced by using allowlisted client methods and tests that deny mutation tools.

---

## 5. Orchestrator Flow

```mermaid
flowchart TD
    Start["run_scan"] --> Context["Create run_id + correlation_id"]
    Context --> Trace["Langfuse trace context"]
    Trace --> K8S["collect.kubernetes"]
    Trace --> Helm["collect.helm"]
    K8S --> Normalize["normalize"]
    Helm --> Normalize
    Normalize --> Hash["hash"]
    Hash --> Detect["detect_changes"]
    Detect --> Sinks["write_sinks"]
    Sinks --> Memory["write_memory"]
    Memory --> Summary["Build ScanSummary"]
    Summary --> End["Return REST/MCP response"]
```

The returned summary includes `trace_ids.langfuse` when Langfuse is enabled and initialized.

---

## 6. Sink Router

```mermaid
flowchart TB
    Records["Changed records"] --> Router["Sink router"]
    Router --> PGE{"Postgres enabled?"}
    Router --> CHE{"ClickHouse enabled?"}
    Router --> QDE{"Qdrant enabled?"}
    Router --> RDE{"Redis enabled?"}
    Router --> STE{"Stdout enabled?"}

    PGE -->|"yes"| PG["Postgres write"]
    CHE -->|"yes"| CH["ClickHouse write"]
    QDE -->|"yes"| QD["Qdrant write"]
    RDE -->|"yes"| RD["Redis write"]
    STE -->|"yes"| SO["Stdout write"]
```

Non-strict mode logs sink errors and continues. Strict mode can fail the scan when an enabled sink fails.

---

## 7. Langfuse Implementation

`observability/langfuse.py` is intentionally optional. If Langfuse is disabled, credentials are missing, or the package is unavailable, the agent falls back to a no-op tracer.

```mermaid
flowchart TD
    Settings["Observability settings"] --> Enabled{"LANGFUSE_ENABLED?"}
    Enabled -->|"false"| Noop["NoopLangfuseTracer"]
    Enabled -->|"true"| Creds{"Keys present?"}
    Creds -->|"no"| Noop
    Creds -->|"yes"| Client["Langfuse get_client()"]
    Client --> Trace["start data-ingestion.scan"]
    Trace --> Flush["flush on completion"]
```

Required runtime values:

```text
LANGFUSE_ENABLED=true
LANGFUSE_BASE_URL=http://langfuse-web.bosgenesis.svc.cluster.local:3000
LANGFUSE_PUBLIC_KEY=<secret>
LANGFUSE_SECRET_KEY=<secret>
```

---

## 8. Helm Chart and Deploy Script

Helm values and templates provide the runtime config. `playbook/deploy.sh` can prompt for sink selection or consume environment overrides.

```mermaid
flowchart LR
    User["Operator"] --> Deploy["playbook/deploy.sh"]
    Deploy --> Values["Helm values + runtime --set overrides"]
    Values --> Chart["Helm chart"]
    Chart --> Deployment["Kubernetes Deployment"]
    Deployment --> Pod["Agent pod"]
```

Supported sink selection:

- `all`
- `none`
- comma/space list such as `postgres,clickhouse`
- individual environment overrides such as `POSTGRES_ENABLED=false`

---

## 9. Langflow Files

| File | Type | Behavior |
|---|---|---|
| `langflow/data-ingestion-agent-architecture.json` | Visualization-only | Shows architecture and data flow. |
| `langflow/data-ingestion-agent-status-flow.json` | Working read-only flow | Calls `/health` or `/scan/latest`. |

The working Langflow flow intentionally does not call `/scan/run`.

---

## 10. Test Coverage

Current tests cover:

- Configuration defaults and env override.
- Redaction of secret settings.
- Orchestrator scan summary and trace id propagation.
- MCP policy and client behavior.
- Collectors, normalizers, hashing, change detection.
- Sink adapters and routers.
- API and end-to-end flow tests.
