"""Base MCP client with injectable transport."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import json
import logging
from typing import Any, Protocol

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

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
class StreamableHttpMcpTransport:
    timeout_seconds: float = 30
    sse_read_timeout_seconds: float = 300
    host_header: str | None = None

    async def call_tool(self, endpoint_url: str, tool_name: str, arguments: dict[str, Any]) -> Any:
        timeout = timedelta(seconds=self.timeout_seconds)
        sse_timeout = timedelta(seconds=self.sse_read_timeout_seconds)
        headers = {"Host": self.host_header} if self.host_header else None
        async with streamablehttp_client(
            endpoint_url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_timeout,
        ) as (read_stream, write_stream, _get_session_id):
            async with ClientSession(read_stream, write_stream, read_timeout_seconds=timeout) as session:
                await session.initialize()
                result = await session.call_tool(
                    tool_name,
                    arguments,
                    read_timeout_seconds=timeout,
                )
                return _unwrap_call_tool_result(result)


def _unwrap_call_tool_result(result: Any) -> Any:
    if getattr(result, "isError", False):
        text = _content_text(getattr(result, "content", None))
        raise McpClientError(text or f"MCP tool returned error: {result!r}")

    structured_content = getattr(result, "structuredContent", None)
    if structured_content is not None:
        return _unwrap_result_key(structured_content)

    text = _content_text(getattr(result, "content", None))
    if text:
        try:
            return _unwrap_result_key(json.loads(text))
        except json.JSONDecodeError:
            return text

    return {}


def _content_text(content: Any) -> str:
    if not isinstance(content, list):
        return ""
    chunks = []
    for item in content:
        text = getattr(item, "text", None)
        if text:
            chunks.append(str(text))
    return "\n".join(chunks)


def _unwrap_result_key(payload: Any) -> Any:
    if isinstance(payload, dict) and "result" in payload and len(payload) == 1:
        return payload["result"]
    return payload


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
