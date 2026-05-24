"""Route memory records to memory-capable sinks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from bosgenesis_k8s_data_ingestion_agent.memory.records import MemoryRecord, MemoryType
from bosgenesis_k8s_data_ingestion_agent.models import RunContext, SinkResult
from bosgenesis_k8s_data_ingestion_agent.observability import get_logger


class MemorySink(Protocol):
    name: str
    enabled: bool

    async def write_memory(
        self,
        run_context: RunContext,
        memory_records: list[MemoryRecord],
    ) -> SinkResult:
        """Write prebuilt memory records."""


@dataclass
class MemoryRouter:
    sinks: list[MemorySink]
    enabled_types: frozenset[MemoryType] = frozenset(
        {MemoryType.SESSION, MemoryType.EPISODIC, MemoryType.SEMANTIC}
    )

    async def route(
        self,
        run_context: RunContext,
        memory_records: list[MemoryRecord],
    ) -> list[SinkResult]:
        logger = get_logger(__name__)
        routed_records = [
            record for record in memory_records if record.memory_type in self.enabled_types
        ]
        results: list[SinkResult] = []
        for sink in self.sinks:
            if not sink.enabled:
                continue
            logger.info(
                "memory sink write started",
                extra={
                    "event": "memory_sink_write_start",
                    "sink_name": sink.name,
                    "run_id": str(run_context.run_id),
                    "memory_records_attempted": len(routed_records),
                },
            )
            result = await sink.write_memory(run_context, routed_records)
            logger.info(
                "memory sink write completed",
                extra={
                    "event": "memory_sink_write_success",
                    "sink_name": sink.name,
                    "run_id": str(run_context.run_id),
                    "memory_records_written": result.records_written,
                },
            )
            results.append(result)
        return results

