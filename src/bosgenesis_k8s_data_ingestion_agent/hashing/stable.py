"""Stable content hash algorithm."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

from bosgenesis_k8s_data_ingestion_agent.models import Observation


VOLATILE_FIELDS = {
    "observed_at",
    "collection_timestamp",
    "run_id",
    "correlation_id",
    "resourceVersion",
    "resource_version",
    "managedFields",
    "managed_fields",
    "lastTransitionTime",
    "last_transition_time",
}


def remove_volatile_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: remove_volatile_fields(item)
            for key, item in value.items()
            if key not in VOLATILE_FIELDS
        }
    if isinstance(value, list):
        return [remove_volatile_fields(item) for item in value]
    return value


def compute_content_hash(payload: dict[str, Any]) -> str:
    stable_payload = remove_volatile_fields(deepcopy(payload))
    serialized = json.dumps(stable_payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def hash_observations(observations: list[Observation]) -> list[Observation]:
    return [observation.with_content_hash(compute_content_hash(observation.hash_input)) for observation in observations]

