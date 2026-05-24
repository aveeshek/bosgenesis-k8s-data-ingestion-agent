# MCP Clients Module Specification

## Role

MCP clients will wrap remote calls to BOS Genesis Kubernetes Inspector MCP and Helm Manager MCP.

## Responsibilities

- Maintain explicit read-tool allowlists.
- Maintain explicit mutation-tool denylists.
- Apply timeouts and retry policy.
- Attach run and trace metadata to calls.
- Normalize transport errors into domain errors.

## Kubernetes read allowlist

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

## Helm read allowlist

- `helm_list_releases`
- `helm_release_status`
- `helm_release_history`
- `helm_get_values`
- `helm_get_manifest`
- `helm_show_chart`
- `helm_template_chart`
- `helm_repo_list`

