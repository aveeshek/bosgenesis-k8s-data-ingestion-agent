"""Kubernetes payload normalization."""

from __future__ import annotations

from typing import Any

from bosgenesis_k8s_data_ingestion_agent.models import Observation, RawBundle, RunContext
from bosgenesis_k8s_data_ingestion_agent.normalizers.common import item_list, make_observation, metadata


K8S_COLLECTION_TYPES = {
    "pods": "Pod",
    "deployments": "Deployment",
    "statefulsets": "StatefulSet",
    "services": "Service",
    "ingresses": "Ingress",
    "pvcs": "PersistentVolumeClaim",
    "events": "Event",
}


def _name(item: dict[str, Any]) -> str:
    meta = metadata(item)
    return str(meta.get("name") or item.get("name") or "unknown")


def _uid(item: dict[str, Any]) -> str | None:
    uid = metadata(item).get("uid") or item.get("uid")
    return str(uid) if uid else None


def _status(item: dict[str, Any]) -> str | None:
    status = item.get("status")
    if isinstance(status, dict):
        phase = status.get("phase")
        if phase:
            return str(phase)
        conditions = status.get("conditions")
        if isinstance(conditions, list) and conditions:
            condition = conditions[-1]
            if isinstance(condition, dict):
                return str(condition.get("type") or condition.get("reason") or "condition")
    return item.get("type") or item.get("reason")


def normalize_k8s_bundle(bundle: RawBundle, run_context: RunContext) -> list[Observation]:
    observations: list[Observation] = []
    for collection_name, entity_type in K8S_COLLECTION_TYPES.items():
        for item in item_list(bundle.payload.get(collection_name, {})):
            name = _name(item)
            normalized = {
                "api_version": item.get("apiVersion"),
                "kind": item.get("kind") or entity_type,
                "metadata": metadata(item),
                "spec": item.get("spec", {}),
                "status": item.get("status", {}),
                "reason": item.get("reason"),
                "type": item.get("type"),
            }
            observations.append(
                make_observation(
                    run_context=run_context,
                    source=bundle.source,
                    namespace=bundle.namespace,
                    entity_type=entity_type,
                    entity_name=name,
                    entity_uid=_uid(item),
                    raw_payload=item,
                    normalized_payload=normalized,
                    status_summary=_status(item),
                )
            )
    return observations

