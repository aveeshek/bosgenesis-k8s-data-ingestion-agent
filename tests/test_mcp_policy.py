import pytest

from bosgenesis_k8s_data_ingestion_agent.errors import ToolDeniedError
from bosgenesis_k8s_data_ingestion_agent.mcp_clients import K8S_READ_TOOLS, MUTATION_DENYLIST, McpToolPolicy


def test_policy_allows_read_tool():
    McpToolPolicy(K8S_READ_TOOLS).assert_allowed("k8s_list_pods")


def test_policy_denies_mutation_tool():
    with pytest.raises(ToolDeniedError):
        McpToolPolicy(K8S_READ_TOOLS).assert_allowed("k8s_delete_resource")


def test_policy_denies_unknown_tool():
    with pytest.raises(ToolDeniedError):
        McpToolPolicy(K8S_READ_TOOLS).assert_allowed("k8s_list_secrets")


def test_mutation_denylist_contains_helm_upgrade():
    assert "helm_upgrade_release" in MUTATION_DENYLIST

