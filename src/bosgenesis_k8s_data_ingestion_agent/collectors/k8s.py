"""Kubernetes raw collection logic."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bosgenesis_k8s_data_ingestion_agent.mcp_clients import K8sInspectorClient
from bosgenesis_k8s_data_ingestion_agent.models import RawBundle, RunContext, ScanRequest


@dataclass
class KubernetesCollector:
    client: K8sInspectorClient

    async def collect(self, request: ScanRequest, run_context: RunContext) -> RawBundle:
        namespace = request.namespace
        payload: dict[str, Any] = {
            "namespace_summary": await self.client.call_tool(
                "k8s_namespace_summary", {"namespace": namespace}, run_context
            ),
            "pods": await self.client.call_tool("k8s_list_pods", {"namespace": namespace}, run_context),
            "deployments": await self.client.call_tool(
                "k8s_list_deployments", {"namespace": namespace}, run_context
            ),
            "statefulsets": await self.client.call_tool(
                "k8s_list_statefulsets", {"namespace": namespace}, run_context
            ),
            "services": await self.client.call_tool(
                "k8s_list_services", {"namespace": namespace}, run_context
            ),
            "ingresses": await self.client.call_tool(
                "k8s_list_ingresses", {"namespace": namespace}, run_context
            ),
            "pvcs": await self.client.call_tool("k8s_list_pvcs", {"namespace": namespace}, run_context),
            "events": await self.client.call_tool(
                "k8s_list_events", {"namespace": namespace}, run_context
            ),
        }
        if request.include_logs:
            payload["logs"] = await self.client.call_tool(
                "k8s_get_pod_logs", {"namespace": namespace, "tail_lines": 200}, run_context
            )
        return RawBundle(source="k8s_mcp", namespace=namespace, payload=payload)

