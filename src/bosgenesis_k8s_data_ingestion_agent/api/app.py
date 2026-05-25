"""REST API surface."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict

from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.models import ScanRequest
from bosgenesis_k8s_data_ingestion_agent.api.mcp import create_mcp_server


def create_app(settings: Settings, orchestrator: ScanOrchestrator):
    from fastapi import FastAPI

    latest_summary = {"value": None}
    mcp_server = create_mcp_server(settings, orchestrator, latest_summary)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _ = app
        async with mcp_server.session_manager.run():
            yield

    app = FastAPI(
        title="BOS Genesis K8s Data Ingestion Agent",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health():
        return {
            "status": "ok",
            "namespace": settings.agent.namespace,
            "components": settings.effective_safe_dict(),
            "mcp_endpoint": "/mcp",
        }

    @app.post("/scan/run")
    async def run_scan(payload: dict | None = None):
        payload = payload or {}
        request = ScanRequest(
            trigger_type=payload.get("trigger_type", "manual"),
            namespace=payload.get("namespace", settings.agent.namespace),
            triggered_by=payload.get("triggered_by", "manual"),
            include_logs=bool(payload.get("include_logs", False)),
            include_manifests=bool(payload.get("include_manifests", False)),
            include_values=bool(payload.get("include_values", False)),
            stream_result=bool(payload.get("stream_result", False)),
        )
        summary = await orchestrator.run_scan(request)
        latest_summary["value"] = summary
        return asdict(summary)

    @app.get("/scan/latest")
    async def latest():
        summary = latest_summary["value"]
        return None if summary is None else asdict(summary)

    @app.get("/config/effective")
    async def effective_config():
        return settings.effective_safe_dict()

    app.mount("/", mcp_server.streamable_http_app(), name="mcp")

    return app
