"""Stdout sink for fallback and local inspection."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import time

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary, SinkResult


@dataclass
class StdoutSink:
    enabled: bool = True
    name: str = "stdout"
    emitted_lines: list[str] = field(default_factory=list)

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        started = time.perf_counter()
        for record in records:
            payload = {
                "run_id": str(run_context.run_id),
                "correlation_id": run_context.correlation_id,
                "namespace": record.observation.namespace,
                "source": record.observation.source,
                "entity_type": record.observation.entity_type,
                "entity_name": record.observation.entity_name,
                "entity_key": record.observation.entity_key,
                "change_type": record.change_type.value,
                "content_hash": record.observation.content_hash,
            }
            self.emitted_lines.append(json.dumps(payload, sort_keys=True))
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(records),
            records_written=len(records),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

