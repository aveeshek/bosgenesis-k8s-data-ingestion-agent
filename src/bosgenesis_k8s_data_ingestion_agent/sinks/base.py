"""Sink base contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary, SinkResult


class BaseSink(Protocol):
    name: str
    enabled: bool

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        """Write change records and optionally a run summary."""


@dataclass
class DisabledSink:
    name: str
    enabled: bool = False

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        return SinkResult(
            sink_name=self.name,
            status="disabled",
            records_attempted=0,
            records_written=0,
            latency_ms=0,
        )

