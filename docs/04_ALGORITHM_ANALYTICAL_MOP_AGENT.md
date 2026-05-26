# BOS Genesis K8s Data Ingestion Agent - Algorithm Design

**Document status:** Implemented baseline

---

## 1. Core Scan Algorithm

```text
trigger scan
  -> create run context
  -> start Langfuse trace when enabled
  -> collect Kubernetes state through K8s MCP
  -> collect Helm state through Helm MCP
  -> normalize records
  -> compute stable hashes
  -> detect changed records
  -> write enabled sinks
  -> write memory records
  -> close trace
  -> return scan summary
```

```mermaid
flowchart TD
    Start([Start]) --> Context["Create run_id and correlation_id"]
    Context --> Trace["Open Langfuse trace"]
    Trace --> K8S["Collect K8s via MCP"]
    Trace --> Helm["Collect Helm via MCP"]
    K8S --> Normalize["Normalize"]
    Helm --> Normalize
    Normalize --> Hash["Stable hash"]
    Hash --> Detect["Detect changes"]
    Detect --> Sink["Write enabled sinks"]
    Sink --> Memory["Write memory records"]
    Memory --> Summary["Build summary"]
    Summary --> Close["Flush/close trace"]
    Close --> End([Return])
```

---

## 2. Trigger Algorithm

```mermaid
flowchart LR
    REST["POST /scan/run"] --> Run["run_scan"]
    MCP["data_ingestion_run_scan"] --> Run
    Startup["run_on_startup"] --> Run
    Scheduler["interval loop"] --> Run
```

Inputs:

- `trigger_type`
- `triggered_by`
- `include_logs`
- `include_manifests`
- `include_values`
- `stream_result`

Defaults keep heavy data collection disabled.

---

## 3. Kubernetes Collection

```mermaid
flowchart TD
    Start([K8s collection]) --> Summary["k8s_namespace_summary"]
    Summary --> Pods["k8s_list_pods"]
    Pods --> Services["k8s_list_services"]
    Services --> Deployments["k8s_list_deployments"]
    Deployments --> Statefulsets["k8s_list_statefulsets"]
    Statefulsets --> Ingresses["k8s_list_ingresses"]
    Ingresses --> Events["k8s_list_events"]
    Events --> Logs{"include_logs?"}
    Logs -->|"yes"| PodLogs["bounded k8s_get_pod_logs"]
    Logs -->|"no"| Bundle["K8s bundle"]
    PodLogs --> Bundle
```

The collector uses MCP read tools only. It does not access Secrets and does not call mutation tools.

---

## 4. Helm Collection

```mermaid
flowchart TD
    Start([Helm collection]) --> Releases["helm_list_releases"]
    Releases --> Loop{"for release"}
    Loop --> Status["helm_release_status"]
    Status --> History["helm_release_history"]
    History --> Values{"include_values?"}
    Values -->|"yes"| GetValues["helm_get_values"]
    Values -->|"no"| Manifest{"include_manifests?"}
    GetValues --> Manifest
    Manifest -->|"yes"| GetManifest["helm_get_manifest"]
    Manifest -->|"no"| Add["Add release records"]
    GetManifest --> Add
    Add --> More{"more releases?"}
    More -->|"yes"| Loop
    More -->|"no"| Repo["helm_repo_list"]
```

The agent does not call Helm install, upgrade, rollback, uninstall, or repository mutation tools.

---

## 5. Normalization and Hashing

```mermaid
flowchart LR
    Raw["Raw MCP payload"] --> Normalize["Canonical observation"]
    Normalize --> Prune["Remove volatile fields"]
    Prune --> Serialize["JSON dumps sorted keys"]
    Serialize --> SHA["SHA-256"]
```

Hash excludes fields that do not represent meaningful state, such as collection timestamp, run id, and correlation id.

---

## 6. Change Detection

```mermaid
flowchart TD
    Obs["Observation + hash"] --> Key["Build entity key"]
    Key --> Latest{"Latest hash available?"}
    Latest -->|"yes"| Compare{"Same hash?"}
    Latest -->|"no"| Changed["Mark changed"]
    Compare -->|"yes"| Skip["Skip duplicate"]
    Compare -->|"no"| Changed
    Changed --> Event["Create change record"]
```

Entity key format:

```text
namespace/source/entity_type/entity_name
```

---

## 7. Sink Write Algorithm

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant R as Sink Router
    participant P as Postgres
    participant C as ClickHouse
    participant Q as Qdrant
    participant D as Redis

    O->>R: changed records + summary
    R->>P: write if enabled
    R->>C: write if enabled
    R->>Q: write if enabled
    R->>D: write if enabled
    R-->>O: sink results
```

In non-strict mode, a sink failure is recorded but does not fail the whole scan.

---

## 8. Langfuse Trace Algorithm

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant T as LangfuseTracer
    participant L as Langfuse

    O->>T: scan(run context)
    T->>L: create root trace data-ingestion.scan
    O->>T: span collect.kubernetes
    O->>T: span collect.helm
    O->>T: span normalize
    O->>T: span hash
    O->>T: span detect_changes
    O->>T: span write_sinks
    O->>T: span write_memory
    T->>L: flush
    T-->>O: trace id
```

The trace id is returned as:

```json
{
  "trace_ids": {
    "langfuse": "..."
  }
}
```

---

## 9. Deploy Sink Selection Algorithm

`playbook/deploy.sh` defaults to all major sinks enabled. In interactive mode it can prompt for sink selection.

```mermaid
flowchart TD
    Start["deploy.sh"] --> Env{"SINKS_ENABLED set?"}
    Env -->|"yes"| Parse["Parse all/none/list"]
    Env -->|"no"| TTY{"Interactive terminal?"}
    TTY -->|"yes"| Prompt["Prompt operator"]
    TTY -->|"no"| Defaults["Use defaults"]
    Prompt --> Overrides["Build Helm --set overrides"]
    Parse --> Overrides
    Defaults --> Overrides
    Overrides --> Helm["helm upgrade --install"]
```

---

## 10. Langflow Working Flow Algorithm

```mermaid
flowchart LR
    Langflow["Langflow custom component"] --> Choice{"endpoint"}
    Choice -->|"health"| Health["GET /health"]
    Choice -->|"latest_scan"| Latest["GET /scan/latest"]
    Health --> Output["Data output JSON"]
    Latest --> Output
```

This working flow is intentionally read-only and does not call `/scan/run`.
