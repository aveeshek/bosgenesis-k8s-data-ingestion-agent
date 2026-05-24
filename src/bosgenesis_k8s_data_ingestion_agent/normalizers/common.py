"""Normalizer helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.models import Observation, RunContext
from bosgenesis_k8s_data_ingestion_agent.security import redact_sensitive


def item_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "resources", "pods", "services", "deployments", "releases"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def metadata(item: dict[str, Any]) -> dict[str, Any]:
    meta = item.get("metadata")
    return meta if isinstance(meta, dict) else {}


def make_observation(
    run_context: RunContext,
    source: str,
    namespace: str,
    entity_type: str,
    entity_name: str,
    raw_payload: dict[str, Any],
    normalized_payload: dict[str, Any],
    status_summary: str | None = None,
    entity_uid: str | None = None,
) -> Observation:
    clean_raw = redact_sensitive(raw_payload)
    clean_normalized = redact_sensitive(normalized_payload)
    return Observation(
        observation_id=uuid4(),
        run_id=run_context.run_id,
        source=source,
        namespace=namespace,
        entity_type=entity_type,
        entity_name=entity_name,
        entity_uid=entity_uid,
        observed_at=datetime.now(UTC),
        status_summary=status_summary,
        raw_payload=clean_raw,
        normalized_payload=clean_normalized,
        hash_input=clean_normalized,
    )

