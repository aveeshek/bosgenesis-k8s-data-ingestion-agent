# MCP Clients Module Specification

## Implemented status

MCP clients wrap Kubernetes Inspector and Helm Manager calls through an injectable transport.

## Implemented responsibilities

- Explicit read-tool allowlists.
- Explicit mutation-tool denylist.
- `McpToolPolicy.assert_allowed()` enforcement before transport calls.
- Run-context argument enrichment with namespace and correlation ID.
- Structured logs around MCP call start/success/failure.
- `InMemoryMcpTransport` for unit and in-process e2e tests.
- `StreamableHttpMcpTransport` for live MCP calls through streamable HTTP.
- Optional MCP `Host` header override for BOS Genesis MCP servers that enforce allowed hostnames while being called through ClusterIP services.
- MCP tool result unwrapping for structured content, JSON text content, and single-key `result` wrappers.
- Transport errors normalized into `McpClientError`.

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
