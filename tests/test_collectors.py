import asyncio

from bosgenesis_k8s_data_ingestion_agent.collectors import HelmCollector, KubernetesCollector
from bosgenesis_k8s_data_ingestion_agent.mcp_clients import (
    HelmManagerClient,
    InMemoryMcpTransport,
    K8sInspectorClient,
)
from bosgenesis_k8s_data_ingestion_agent.models import RunContext, ScanRequest


def test_kubernetes_collector_calls_expected_read_tools():
    asyncio.run(_test_kubernetes_collector_calls_expected_read_tools())


async def _test_kubernetes_collector_calls_expected_read_tools():
    transport = InMemoryMcpTransport(
        responses={
            "k8s_namespace_summary": {},
            "k8s_list_pods": {"items": []},
            "k8s_list_deployments": {"items": []},
            "k8s_list_statefulsets": {"items": []},
            "k8s_list_services": {"items": []},
            "k8s_list_ingresses": {"items": []},
            "k8s_list_pvcs": {"items": []},
            "k8s_list_events": {"items": []},
        }
    )
    collector = KubernetesCollector(K8sInspectorClient("http://k8s/mcp", transport))

    bundle = await collector.collect(ScanRequest(), RunContext())

    assert bundle.source == "k8s_mcp"
    assert "pods" in bundle.payload
    assert "k8s_get_pod_logs" not in [call[1] for call in transport.calls]


def test_helm_collector_collects_release_details():
    asyncio.run(_test_helm_collector_collects_release_details())


async def _test_helm_collector_collects_release_details():
    transport = InMemoryMcpTransport(
        responses={
            "helm_list_releases": {"releases": [{"name": "demo"}]},
            "helm_release_status": {"status": "deployed"},
            "helm_release_history": [{"revision": 1}],
            "helm_repo_list": [],
        }
    )
    collector = HelmCollector(HelmManagerClient("http://helm/mcp", transport))

    bundle = await collector.collect(ScanRequest(), RunContext())

    assert bundle.source == "helm_mcp"
    assert bundle.payload["releases"][0]["status"]["status"] == "deployed"


def test_helm_collector_accepts_live_manager_output_shape():
    asyncio.run(_test_helm_collector_accepts_live_manager_output_shape())


async def _test_helm_collector_accepts_live_manager_output_shape():
    transport = InMemoryMcpTransport(
        responses={
            "helm_list_releases": {"status": "ok", "output": [{"name": "clickhouse"}]},
            "helm_release_status": {"status": "deployed"},
            "helm_release_history": [{"revision": 1}],
            "helm_repo_list": [],
        }
    )
    collector = HelmCollector(HelmManagerClient("http://helm/mcp", transport))

    bundle = await collector.collect(ScanRequest(), RunContext())

    assert bundle.payload["releases"][0]["release"]["name"] == "clickhouse"
