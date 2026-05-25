"""MCP tool surface for the data ingestion agent."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.models import ScanRequest


def create_mcp_server(
    settings: Settings,
    orchestrator: ScanOrchestrator,
    latest_summary: dict[str, Any],
) -> FastMCP:
    mcp = FastMCP(
        "bosgenesis-k8s-data-ingestion-agent",
        streamable_http_path="/mcp",
        transport_security=TransportSecuritySettings(
            allowed_hosts=list(settings.api.mcp_allowed_hosts),
        ),
    )

    @mcp.tool()
    def data_ingestion_health(actor: str = "codex") -> dict[str, Any]:
        """Return agent health and safe effective configuration."""
        return {
            "status": "ok",
            "actor": actor,
            "namespace": settings.agent.namespace,
            "mcp_endpoint": "/mcp",
            "components": settings.effective_safe_dict(),
        }

    @mcp.tool()
    async def data_ingestion_run_scan(
        trigger_type: str = "manual",
        triggered_by: str = "mcp",
        include_logs: bool = False,
        include_manifests: bool = False,
        include_values: bool = False,
        stream_result: bool = False,
        actor: str = "codex",
    ) -> dict[str, Any]:
        """Run an on-demand ingestion scan in the configured namespace."""
        request = ScanRequest(
            trigger_type=trigger_type,
            namespace=settings.agent.namespace,
            triggered_by=triggered_by or actor,
            include_logs=include_logs,
            include_manifests=include_manifests,
            include_values=include_values,
            stream_result=stream_result,
        )
        summary = await orchestrator.run_scan(request)
        latest_summary["value"] = summary
        return asdict(summary)

    @mcp.tool()
    def data_ingestion_latest_scan(actor: str = "codex") -> dict[str, Any] | None:
        """Return the latest in-memory scan summary, if one exists."""
        _ = actor
        summary = latest_summary["value"]
        return None if summary is None else asdict(summary)

    @mcp.tool()
    def data_ingestion_effective_config(actor: str = "codex") -> dict[str, Any]:
        """Return the safe effective configuration."""
        _ = actor
        return settings.effective_safe_dict()

    return mcp
