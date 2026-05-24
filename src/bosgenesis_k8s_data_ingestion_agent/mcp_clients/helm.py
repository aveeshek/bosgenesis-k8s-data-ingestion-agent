"""Helm Manager MCP client."""

from __future__ import annotations

from bosgenesis_k8s_data_ingestion_agent.mcp_clients.base import BaseMcpClient, McpTransport
from bosgenesis_k8s_data_ingestion_agent.mcp_clients.policy import HELM_READ_TOOLS, McpToolPolicy
from bosgenesis_k8s_data_ingestion_agent.observability import get_logger


class HelmManagerClient(BaseMcpClient):
    def __init__(self, endpoint_url: str, transport: McpTransport):
        super().__init__(
            endpoint_url=endpoint_url,
            policy=McpToolPolicy(HELM_READ_TOOLS),
            transport=transport,
            logger=get_logger(__name__),
        )

