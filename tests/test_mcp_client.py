import asyncio

from bosgenesis_k8s_data_ingestion_agent.mcp_clients import InMemoryMcpTransport, K8sInspectorClient
from bosgenesis_k8s_data_ingestion_agent.mcp_clients.base import _unwrap_call_tool_result
from bosgenesis_k8s_data_ingestion_agent.models import RunContext


class DummyTextContent:
    def __init__(self, text):
        self.text = text


class DummyCallToolResult:
    def __init__(self, content=None, structured_content=None, is_error=False):
        self.content = content
        self.structuredContent = structured_content
        self.isError = is_error


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


def test_unwrap_call_tool_result_prefers_structured_content():
    result = DummyCallToolResult(structured_content={"result": [{"name": "pod-a"}]})

    assert _unwrap_call_tool_result(result) == [{"name": "pod-a"}]


def test_unwrap_call_tool_result_parses_text_json():
    result = DummyCallToolResult(content=[DummyTextContent('{"items":[{"name":"pod-a"}]}')])

    assert _unwrap_call_tool_result(result) == {"items": [{"name": "pod-a"}]}


def test_unwrap_call_tool_result_raises_on_mcp_error():
    result = DummyCallToolResult(content=[DummyTextContent("boom")], is_error=True)

    try:
        _unwrap_call_tool_result(result)
    except Exception as error:
        assert "boom" in str(error)
    else:
        raise AssertionError("expected MCP error")
