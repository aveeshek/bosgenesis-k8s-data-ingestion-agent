"""Hash-based change detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, ChangeType, Observation


class HashStateStore(Protocol):
    def get_latest_hash(self, namespace: str, source: str, entity_key: str) -> str | None:
        """Return latest known hash."""

    def set_latest_hash(self, namespace: str, source: str, entity_key: str, content_hash: str) -> None:
        """Persist latest known hash."""


@dataclass
class InMemoryHashStateStore:
    hashes: dict[tuple[str, str, str], str] = field(default_factory=dict)

    def get_latest_hash(self, namespace: str, source: str, entity_key: str) -> str | None:
        return self.hashes.get((namespace, source, entity_key))

    def set_latest_hash(self, namespace: str, source: str, entity_key: str, content_hash: str) -> None:
        self.hashes[(namespace, source, entity_key)] = content_hash


@dataclass
class ChangeDetector:
    store: HashStateStore | None = None
    full_history: bool = False

    def detect(self, observations: list[Observation]) -> list[ChangeRecord]:
        records: list[ChangeRecord] = []
        for observation in observations:
            if not observation.content_hash:
                raise ValueError("observation must have content_hash before change detection")
            previous_hash = (
                self.store.get_latest_hash(
                    observation.namespace, observation.source, observation.entity_key
                )
                if self.store
                else None
            )
            if previous_hash is None:
                change_type = ChangeType.NEW
            elif previous_hash == observation.content_hash and not self.full_history:
                change_type = ChangeType.UNCHANGED
            else:
                change_type = ChangeType.CHANGED
            if self.store and change_type in {ChangeType.NEW, ChangeType.CHANGED}:
                self.store.set_latest_hash(
                    observation.namespace,
                    observation.source,
                    observation.entity_key,
                    observation.content_hash,
                )
            records.append(
                ChangeRecord(
                    observation=observation,
                    change_type=change_type,
                    previous_hash=previous_hash,
                )
            )
        return records

