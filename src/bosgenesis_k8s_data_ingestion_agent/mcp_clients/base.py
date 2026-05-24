"""Base MCP client with injectable transport."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Protocol

from bosgenesis_k8s_data_ingestion_agent.errors import McpClientError
from bosgenesis_k8s_data_ingestion_agent.mcp_clients.policy import McpToolPolicy
from bosgenesis_k8s_data_ingestion_agent.models import RunContext


class McpTransport(Protocol):
    async def call_tool(self, endpoint_url: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Call a remote MCP tool."""


@dataclass
class InMemoryMcpTransport:
    responses: dict[str, Any] = field(default_factory=dict)
    calls: list[tuple[str, str, dict[str, Any]]] = field(default_factory=list)

    async def call_tool(self, endpoint_url: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        self.calls.append((endpoint_url, tool_name, arguments))
        response = self.responses.get(tool_name)
        if isinstance(response, Exception):
            raise response
        return response if response is not None else {}


@dataclass
class BaseMcpClient:
    endpoint_url: str
    policy: McpToolPolicy
    transport: McpTransport
    logger: logging.Logger

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        run_context: RunContext | None = None,
    ) -> Any:
        self.policy.assert_allowed(tool_name)
        enriched_args = dict(arguments)
        if run_context:
            enriched_args.setdefault("namespace", run_context.namespace)
            enriched_args.setdefault("correlation_id", run_context.correlation_id)
        self.logger.info(
            "calling mcp tool",
            extra={
                "event": "mcp_call_start",
                "tool_name": tool_name,
                "endpoint_url": self.endpoint_url,
                "run_id": str(run_context.run_id) if run_context else None,
                "correlation_id": run_context.correlation_id if run_context else None,
            },
        )
        try:
            result = await self.transport.call_tool(self.endpoint_url, tool_name, enriched_args)
        except Exception as error:  # pragma: no cover - exact transport failures vary
            self.logger.exception(
                "mcp tool failed",
                extra={
                    "event": "mcp_call_failed",
                    "tool_name": tool_name,
                    "endpoint_url": self.endpoint_url,
                },
            )
            raise McpClientError(str(error)) from error
        self.logger.info(
            "mcp tool completed",
            extra={"event": "mcp_call_success", "tool_name": tool_name},
        )
        return result

