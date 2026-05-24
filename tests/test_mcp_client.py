import asyncio

from bosgenesis_k8s_data_ingestion_agent.mcp_clients import InMemoryMcpTransport, K8sInspectorClient
from bosgenesis_k8s_data_ingestion_agent.models import RunContext


def test_client_enriches_call_with_run_context():
    asyncio.run(_test_client_enriches_call_with_run_context())


async def _test_client_enriches_call_with_run_context():
    transport = InMemoryMcpTransport(responses={"k8s_list_pods": {"items": []}})
    client = K8sInspectorClient("http://example/mcp", transport)
    context = RunContext(namespace="bosgenesis")

    result = await client.call_tool("k8s_list_pods", {}, context)

    assert result == {"items": []}
    _, tool_name, arguments = transport.calls[0]
    assert tool_name == "k8s_list_pods"
    assert arguments["namespace"] == "bosgenesis"
    assert arguments["correlation_id"] == context.correlation_id
