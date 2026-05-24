"""Sink routing."""

from __future__ import annotations

from dataclasses import dataclass
import time

from bosgenesis_k8s_data_ingestion_agent.errors import SinkWriteError
from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary, SinkResult
from bosgenesis_k8s_data_ingestion_agent.observability import get_logger
from bosgenesis_k8s_data_ingestion_agent.sinks.base import BaseSink


@dataclass
class SinkRouter:
    sinks: list[BaseSink]
    strict: bool = False

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> list[SinkResult]:
        logger = get_logger(__name__)
        enabled_sinks = [sink for sink in self.sinks if sink.enabled]
        results: list[SinkResult] = []
        for sink in enabled_sinks:
            started = time.perf_counter()
            logger.info(
                "sink write started",
                extra={
                    "event": "sink_write_start",
                    "sink_name": sink.name,
                    "run_id": str(run_context.run_id),
                    "correlation_id": run_context.correlation_id,
                    "records_attempted": len(records),
                },
            )
            try:
                result = await sink.write(run_context, records, summary)
            except Exception as error:
                result = SinkResult(
                    sink_name=sink.name,
                    status="failed",
                    records_attempted=len(records),
                    records_written=0,
                    latency_ms=int((time.perf_counter() - started) * 1000),
                    error=str(error),
                )
                logger.exception(
                    "sink write failed",
                    extra={
                        "event": "sink_write_failed",
                        "sink_name": sink.name,
                        "run_id": str(run_context.run_id),
                    },
                )
                results.append(result)
                if self.strict:
                    raise SinkWriteError(f"sink {sink.name} failed: {error}") from error
            else:
                logger.info(
                    "sink write completed",
                    extra={
                        "event": "sink_write_success",
                        "sink_name": sink.name,
                        "run_id": str(run_context.run_id),
                        "records_written": result.records_written,
                        "latency_ms": result.latency_ms,
                    },
                )
                results.append(result)
        return results

