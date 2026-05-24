"""Shared domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4


class ScanStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


class ChangeType(StrEnum):
    NEW = "new"
    CHANGED = "changed"
    UNCHANGED = "unchanged"
    DELETED_CANDIDATE = "deleted_candidate"


@dataclass(frozen=True)
class ScanRequest:
    trigger_type: str = "manual"
    namespace: str = "bosgenesis"
    triggered_by: str = "manual"
    include_logs: bool = False
    include_manifests: bool = False
    include_values: bool = False
    stream_result: bool = False


@dataclass(frozen=True)
class RunContext:
    run_id: UUID = field(default_factory=uuid4)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    namespace: str = "bosgenesis"
    trigger_type: str = "manual"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class RawBundle:
    source: str
    namespace: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class Observation:
    observation_id: UUID
    run_id: UUID
    source: str
    namespace: str
    entity_type: str
    entity_name: str
    entity_uid: str | None
    observed_at: datetime
    status_summary: str | None
    raw_payload: dict[str, Any]
    normalized_payload: dict[str, Any]
    hash_input: dict[str, Any]
    content_hash: str | None = None

    @property
    def entity_key(self) -> str:
        uid_or_name = self.entity_uid or self.entity_name
        return f"{self.source}:{self.namespace}:{self.entity_type}:{uid_or_name}"

    def with_content_hash(self, content_hash: str) -> "Observation":
        return Observation(
            observation_id=self.observation_id,
            run_id=self.run_id,
            source=self.source,
            namespace=self.namespace,
            entity_type=self.entity_type,
            entity_name=self.entity_name,
            entity_uid=self.entity_uid,
            observed_at=self.observed_at,
            status_summary=self.status_summary,
            raw_payload=self.raw_payload,
            normalized_payload=self.normalized_payload,
            hash_input=self.hash_input,
            content_hash=content_hash,
        )


@dataclass(frozen=True)
class ChangeRecord:
    observation: Observation
    change_type: ChangeType
    previous_hash: str | None = None


@dataclass(frozen=True)
class SinkResult:
    sink_name: str
    status: str
    records_attempted: int
    records_written: int
    latency_ms: int
    error: str | None = None


@dataclass(frozen=True)
class ScanSummary:
    run_id: UUID
    correlation_id: str
    namespace: str
    status: ScanStatus
    started_at: datetime
    finished_at: datetime
    resources_seen: int = 0
    resources_changed: int = 0
    helm_releases_seen: int = 0
    helm_releases_changed: int = 0
    sinks_used: tuple[str, ...] = ()
    trace_ids: dict[str, str | None] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

