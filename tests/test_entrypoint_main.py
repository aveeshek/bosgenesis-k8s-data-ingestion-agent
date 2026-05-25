from bosgenesis_k8s_data_ingestion_agent.config import McpEndpointSettings, Settings
from bosgenesis_k8s_data_ingestion_agent.entrypoints.main import build_orchestrator


def test_build_orchestrator_wires_live_collectors_when_mcp_enabled():
    settings = Settings(
        k8s_mcp=McpEndpointSettings(
            url="http://k8s/mcp",
            host_header="k8s-inspector.bosgenesis.local",
            timeout_seconds=12,
        ),
        helm_mcp=McpEndpointSettings(
            url="http://helm/mcp",
            host_header="helm-manager.bosgenesis.local",
            timeout_seconds=13,
        ),
    )

    orchestrator = build_orchestrator(settings)

    assert orchestrator.k8s_collector is not None
    assert orchestrator.helm_collector is not None
    assert orchestrator.k8s_collector.client.endpoint_url == "http://k8s/mcp"
    assert orchestrator.helm_collector.client.endpoint_url == "http://helm/mcp"
    assert orchestrator.k8s_collector.client.transport.timeout_seconds == 12
    assert orchestrator.helm_collector.client.transport.timeout_seconds == 13
    assert orchestrator.k8s_collector.client.transport.host_header == (
        "k8s-inspector.bosgenesis.local"
    )
    assert orchestrator.helm_collector.client.transport.host_header == (
        "helm-manager.bosgenesis.local"
    )


def test_build_orchestrator_respects_disabled_mcp_collectors():
    settings = Settings(
        k8s_mcp=McpEndpointSettings(enabled=False),
        helm_mcp=McpEndpointSettings(enabled=False),
    )

    orchestrator = build_orchestrator(settings)

    assert orchestrator.k8s_collector is None
    assert orchestrator.helm_collector is None
