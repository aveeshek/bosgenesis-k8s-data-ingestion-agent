"""Helm raw collection logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bosgenesis_k8s_data_ingestion_agent.mcp_clients import HelmManagerClient
from bosgenesis_k8s_data_ingestion_agent.models import RawBundle, RunContext, ScanRequest


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("releases", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


@dataclass
class HelmCollector:
    client: HelmManagerClient

    async def collect(self, request: ScanRequest, run_context: RunContext) -> RawBundle:
        namespace = request.namespace
        releases_payload = await self.client.call_tool(
            "helm_list_releases", {"namespace": namespace}, run_context
        )
        releases = _items(releases_payload)
        release_bundles = []
        for release in releases:
            release_name = release.get("name") or release.get("release_name")
            if not release_name:
                continue
            bundle: dict[str, Any] = {
                "release": release,
                "status": await self.client.call_tool(
                    "helm_release_status",
                    {"namespace": namespace, "release_name": release_name},
                    run_context,
                ),
                "history": await self.client.call_tool(
                    "helm_release_history",
                    {"namespace": namespace, "release_name": release_name},
                    run_context,
                ),
            }
            if request.include_values:
                bundle["values"] = await self.client.call_tool(
                    "helm_get_values",
                    {"namespace": namespace, "release_name": release_name},
                    run_context,
                )
            if request.include_manifests:
                bundle["manifest"] = await self.client.call_tool(
                    "helm_get_manifest",
                    {"namespace": namespace, "release_name": release_name},
                    run_context,
                )
            release_bundles.append(bundle)
        return RawBundle(
            source="helm_mcp",
            namespace=namespace,
            payload={
                "releases": release_bundles,
                "repo_list": await self.client.call_tool("helm_repo_list", {}, run_context),
            },
        )

