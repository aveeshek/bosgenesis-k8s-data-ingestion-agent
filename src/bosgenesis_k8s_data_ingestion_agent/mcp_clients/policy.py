"""MCP read allowlists and mutation denylists."""

from __future__ import annotations

from dataclasses import dataclass

from bosgenesis_k8s_data_ingestion_agent.errors import ToolDeniedError


K8S_READ_TOOLS = frozenset(
    {
        "k8s_namespace_summary",
        "k8s_list_pods",
        "k8s_describe_pod",
        "k8s_get_pod_logs",
        "k8s_list_services",
        "k8s_list_pvcs",
        "k8s_describe_pvc",
        "k8s_list_deployments",
        "k8s_list_statefulsets",
        "k8s_list_ingresses",
        "k8s_list_events",
    }
)

HELM_READ_TOOLS = frozenset(
    {
        "helm_list_releases",
        "helm_release_status",
        "helm_release_history",
        "helm_get_values",
        "helm_get_manifest",
        "helm_show_chart",
        "helm_template_chart",
        "helm_repo_list",
    }
)

MUTATION_DENYLIST = frozenset(
    {
        "k8s_apply_manifest",
        "k8s_create_resource",
        "k8s_update_resource",
        "k8s_delete_resource",
        "k8s_patch_resource",
        "k8s_scale_deployment",
        "helm_install_release",
        "helm_upgrade_release",
        "helm_uninstall_release",
        "helm_rollback_release",
        "helm_repo_add",
        "helm_repo_update",
    }
)


@dataclass(frozen=True)
class McpToolPolicy:
    allowed_tools: frozenset[str]
    denied_tools: frozenset[str] = MUTATION_DENYLIST

    def assert_allowed(self, tool_name: str) -> None:
        if tool_name in self.denied_tools or tool_name not in self.allowed_tools:
            raise ToolDeniedError(f"MCP tool is not allowed for this agent: {tool_name}")

