"""Redis latest-hash and cache sink writer."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary, SinkResult
from bosgenesis_k8s_data_ingestion_agent.sinks.serialization import json_dumps


ClientFactory = Callable[[], Any]


@dataclass
class RedisSink:
    host: str = "redis-master.bosgenesis.svc.cluster.local"
    port: int = 6379
    db: int = 0
    password: str | None = None
    key_prefix: str = "bg:k8s-ingestion"
    run_summary_ttl_seconds: int = 2_592_000
    enabled: bool = True
    client_factory: ClientFactory | None = None
    name: str = "redis"

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        started = time.perf_counter()
        client = self._client()
        try:
            for record in records:
                observation = record.observation
                await client.set(
                    self._latest_hash_key(
                        observation.namespace, observation.source, observation.entity_key
                    ),
                    observation.content_hash or "",
                )
                await client.xadd(
                    f"{self.key_prefix}:stream:changes",
                    {
                        "run_id": str(run_context.run_id),
                        "correlation_id": run_context.correlation_id,
                        "namespace": observation.namespace,
                        "source": observation.source,
                        "entity_type": observation.entity_type,
                        "entity_name": observation.entity_name,
                        "entity_key": observation.entity_key,
                        "change_type": record.change_type.value,
                        "previous_hash": record.previous_hash or "",
                        "current_hash": observation.content_hash or "",
                    },
                )
            if summary:
                summary_payload = json_dumps(summary)
                await client.set(f"{self.key_prefix}:latest-run", str(summary.run_id))
                await client.set(
                    f"{self.key_prefix}:run:{summary.run_id}:summary",
                    summary_payload,
                    ex=self.run_summary_ttl_seconds,
                )
        finally:
            close = getattr(client, "aclose", None) or getattr(client, "close", None)
            if callable(close):
                result = close()
                if hasattr(result, "__await__"):
                    await result
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(records),
            records_written=len(records),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _client(self):
        if self.client_factory:
            return self.client_factory()
        import redis.asyncio as redis

        return redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=True,
        )

    def _latest_hash_key(self, namespace: str, source: str, entity_key: str) -> str:
        safe_entity_key = entity_key.replace(" ", "_")
        return f"{self.key_prefix}:latest-hash:{namespace}:{source}:{safe_entity_key}"
