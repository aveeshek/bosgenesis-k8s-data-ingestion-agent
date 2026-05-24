"""Shared sink serialization helpers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from typing import Any
from uuid import UUID

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, Observation


def to_jsonable(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return value


def json_dumps(value: Any) -> str:
    return json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"))


def is_helm_observation(observation: Observation) -> bool:
    return observation.entity_type == "HelmRelease" or observation.source == "helm_mcp"


def memory_text(record: ChangeRecord) -> str:
    observation = record.observation
    return (
        f"{record.change_type.value} {observation.entity_type} "
        f"{observation.entity_name} in namespace {observation.namespace}; "
        f"status={observation.status_summary or 'unknown'}; "
        f"hash={observation.content_hash or 'missing'}"
    )

