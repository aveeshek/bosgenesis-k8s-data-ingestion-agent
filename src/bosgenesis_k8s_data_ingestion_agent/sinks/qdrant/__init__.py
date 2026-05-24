"""Qdrant semantic memory sink writer."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable
from uuid import uuid5, NAMESPACE_URL

from bosgenesis_k8s_data_ingestion_agent.memory.records import MemoryRecord
from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary, SinkResult
from bosgenesis_k8s_data_ingestion_agent.sinks.serialization import memory_text, to_jsonable


ClientFactory = Callable[[], Any]
EmbeddingFunction = Callable[[str], list[float]]


@dataclass
class QdrantSink:
    url: str = "http://qdrant.bosgenesis.svc.cluster.local:6333"
    collection_name: str = "bosgenesis_k8s_observations"
    vector_size: int = 1536
    api_key: str | None = None
    enabled: bool = True
    client_factory: ClientFactory | None = None
    embedding_function: EmbeddingFunction | None = None
    name: str = "qdrant"

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        started = time.perf_counter()
        client = self._client()
        points = [self._point(record, run_context) for record in records]
        if points:
            client.upsert(collection_name=self.collection_name, points=points)
        close = getattr(client, "close", None)
        if callable(close):
            close()
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(records),
            records_written=len(points),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def write_memory(
        self,
        run_context: RunContext,
        memory_records: list[MemoryRecord],
    ) -> SinkResult:
        started = time.perf_counter()
        client = self._client()
        points = [self._memory_point(record, run_context) for record in memory_records]
        if points:
            client.upsert(collection_name=self.collection_name, points=points)
        close = getattr(client, "close", None)
        if callable(close):
            close()
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(memory_records),
            records_written=len(points),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _client(self):
        if self.client_factory:
            return self.client_factory()
        from qdrant_client import QdrantClient

        return QdrantClient(url=self.url, api_key=self.api_key)

    def _point(self, record: ChangeRecord, run_context: RunContext) -> dict[str, Any]:
        text = memory_text(record)
        observation = record.observation
        point_id = str(uuid5(NAMESPACE_URL, f"{observation.entity_key}:{observation.content_hash}"))
        return {
            "id": point_id,
            "vector": self._embedding(text),
            "payload": {
                "text": text,
                "run_id": str(run_context.run_id),
                "correlation_id": run_context.correlation_id,
                "namespace": observation.namespace,
                "source": observation.source,
                "entity_type": observation.entity_type,
                "entity_name": observation.entity_name,
                "entity_key": observation.entity_key,
                "change_type": record.change_type.value,
                "content_hash": observation.content_hash,
                "observed_at": observation.observed_at.isoformat(),
                "status_summary": observation.status_summary,
                "metadata": to_jsonable(observation.normalized_payload),
            },
        }

    def _memory_point(self, record: MemoryRecord, run_context: RunContext) -> dict[str, Any]:
        point_id = str(uuid5(NAMESPACE_URL, f"{record.memory_type}:{record.entity_key}:{record.content_hash}:{record.run_id}"))
        observed_at = record.observed_at.isoformat() if record.observed_at else None
        return {
            "id": point_id,
            "vector": self._embedding(record.text),
            "payload": {
                "text": record.text,
                "memory_type": record.memory_type.value,
                "run_id": str(record.run_id or run_context.run_id),
                "correlation_id": record.correlation_id or run_context.correlation_id,
                "namespace": record.namespace,
                "source": record.source,
                "entity_type": record.entity_type,
                "entity_name": record.entity_name,
                "entity_key": record.entity_key,
                "content_hash": record.content_hash,
                "observed_at": observed_at,
                "metadata": to_jsonable(record.metadata),
            },
        }

    def _embedding(self, text: str) -> list[float]:
        if self.embedding_function:
            vector = self.embedding_function(text)
            if len(vector) != self.vector_size:
                raise ValueError(
                    f"embedding_function returned {len(vector)} dimensions; expected {self.vector_size}"
                )
            return vector
        return [0.0] * self.vector_size
