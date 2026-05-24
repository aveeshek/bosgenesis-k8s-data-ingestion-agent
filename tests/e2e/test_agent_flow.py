from fastapi.testclient import TestClient

from bosgenesis_k8s_data_ingestion_agent.api import create_app
from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector, InMemoryHashStateStore
from bosgenesis_k8s_data_ingestion_agent.collectors import HelmCollector, KubernetesCollector
from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.mcp_clients import (
    HelmManagerClient,
    InMemoryMcpTransport,
    K8sInspectorClient,
)
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter, StdoutSink


def build_e2e_client():
    k8s_transport = InMemoryMcpTransport(
        responses={
            "k8s_namespace_summary": {"namespace": "bosgenesis", "status": "Active"},
            "k8s_list_pods": {
                "items": [
                    {
                        "apiVersion": "v1",
                        "kind": "Pod",
                        "metadata": {
                            "name": "demo-pod",
                            "uid": "pod-uid-1",
                            "resourceVersion": "100",
                        },
                        "spec": {"containers": [{"name": "app", "image": "demo:1"}]},
                        "status": {"phase": "Running"},
                    }
                ]
            },
            "k8s_list_deployments": {
                "items": [
                    {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "metadata": {
                            "name": "demo-deployment",
                            "uid": "deploy-uid-1",
                            "resourceVersion": "200",
                        },
                        "spec": {"replicas": 1},
                        "status": {"readyReplicas": 1, "availableReplicas": 1},
                    }
                ]
            },
            "k8s_list_statefulsets": {"items": []},
            "k8s_list_services": {"items": []},
            "k8s_list_ingresses": {"items": []},
            "k8s_list_pvcs": {"items": []},
            "k8s_list_events": {"items": []},
        }
    )
    helm_transport = InMemoryMcpTransport(
        responses={
            "helm_list_releases": {"releases": [{"name": "demo-release", "chart": "demo-chart"}]},
            "helm_release_status": {
                "name": "demo-release",
                "status": "deployed",
                "revision": 1,
            },
            "helm_release_history": [{"revision": 1, "status": "deployed"}],
            "helm_repo_list": [],
        }
    )
    stdout_sink = StdoutSink()
    orchestrator = ScanOrchestrator(
        change_detector=ChangeDetector(store=InMemoryHashStateStore()),
        sink_router=SinkRouter([stdout_sink]),
        k8s_collector=KubernetesCollector(K8sInspectorClient("http://k8s/mcp", k8s_transport)),
        helm_collector=HelmCollector(HelmManagerClient("http://helm/mcp", helm_transport)),
    )
    app = create_app(Settings(), orchestrator)
    return TestClient(app), stdout_sink, k8s_transport, helm_transport


def test_on_demand_scan_flows_from_api_to_sink():
    client, stdout_sink, k8s_transport, helm_transport = build_e2e_client()

    response = client.post(
        "/scan/run",
        json={
            "trigger_type": "manual",
            "triggered_by": "e2e-test",
            "namespace": "bosgenesis",
            "include_logs": False,
            "include_manifests": False,
            "include_values": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["namespace"] == "bosgenesis"
    assert payload["resources_seen"] == 3
    assert payload["resources_changed"] == 3
    assert payload["sinks_used"] == ["stdout"]
    assert len(stdout_sink.emitted_lines) == 3
    assert [call[1] for call in k8s_transport.calls] == [
        "k8s_namespace_summary",
        "k8s_list_pods",
        "k8s_list_deployments",
        "k8s_list_statefulsets",
        "k8s_list_services",
        "k8s_list_ingresses",
        "k8s_list_pvcs",
        "k8s_list_events",
    ]
    assert [call[1] for call in helm_transport.calls] == [
        "helm_list_releases",
        "helm_release_status",
        "helm_release_history",
        "helm_repo_list",
    ]


def test_repeated_on_demand_scan_deduplicates_unchanged_records():
    client, stdout_sink, _, _ = build_e2e_client()

    first = client.post("/scan/run", json={"namespace": "bosgenesis"})
    second = client.post("/scan/run", json={"namespace": "bosgenesis"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["resources_changed"] == 3
    assert second.json()["resources_seen"] == 3
    assert second.json()["resources_changed"] == 0
    assert len(stdout_sink.emitted_lines) == 3


def test_latest_scan_endpoint_returns_last_summary():
    client, _, _, _ = build_e2e_client()

    assert client.get("/scan/latest").json() is None
    scan_response = client.post("/scan/run", json={"namespace": "bosgenesis"})
    latest_response = client.get("/scan/latest")

    assert latest_response.status_code == 200
    assert latest_response.json()["run_id"] == scan_response.json()["run_id"]
    assert latest_response.json()["status"] == "success"


def test_health_endpoint_exposes_safe_effective_config():
    client, _, _, _ = build_e2e_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["namespace"] == "bosgenesis"
    assert "components" in payload

