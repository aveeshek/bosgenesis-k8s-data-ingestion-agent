"""Scan lifecycle orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector
from bosgenesis_k8s_data_ingestion_agent.collectors import HelmCollector, KubernetesCollector
from bosgenesis_k8s_data_ingestion_agent.hashing import hash_observations
from bosgenesis_k8s_data_ingestion_agent.memory import MemoryRecordBuilder, MemoryRouter
from bosgenesis_k8s_data_ingestion_agent.models import (
    ChangeType,
    RawBundle,
    RunContext,
    ScanRequest,
    ScanStatus,
    ScanSummary,
)
from bosgenesis_k8s_data_ingestion_agent.normalizers import normalize_all
from bosgenesis_k8s_data_ingestion_agent.observability import NoopLangfuseTracer, get_logger
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter


@dataclass
class ScanOrchestrator:
    change_detector: ChangeDetector
    sink_router: SinkRouter
    k8s_collector: KubernetesCollector | None = None
    helm_collector: HelmCollector | None = None
    memory_record_builder: MemoryRecordBuilder | None = None
    memory_router: MemoryRouter | None = None
    langfuse_tracer: object = NoopLangfuseTracer()

    async def run_scan(self, request: ScanRequest) -> ScanSummary:
        logger = get_logger(__name__)
        run_context = RunContext(namespace=request.namespace, trigger_type=request.trigger_type)
        errors: list[str] = []
        logger.info(
            "scan started",
            extra={
                "event": "scan_start",
                "run_id": str(run_context.run_id),
                "correlation_id": run_context.correlation_id,
                "namespace": request.namespace,
                "trigger_type": request.trigger_type,
            },
        )
        bundles: list[RawBundle] = []
        with self.langfuse_tracer.scan(request, run_context) as trace:
            trace_ids = {"langfuse": trace.trace_id} if trace.trace_id else {}
            try:
                if self.k8s_collector:
                    with trace.span("collect.kubernetes", metadata={"source": "k8s_mcp"}):
                        bundles.append(await self.k8s_collector.collect(request, run_context))
                if self.helm_collector:
                    with trace.span("collect.helm", metadata={"source": "helm_mcp"}):
                        bundles.append(await self.helm_collector.collect(request, run_context))
                with trace.span("normalize", metadata={"bundles": len(bundles)}):
                    observations = normalize_all(bundles, run_context)
                with trace.span("hash", metadata={"observations": len(observations)}):
                    hashed = hash_observations(observations)
                with trace.span("detect_changes", metadata={"observations": len(hashed)}):
                    changes = self.change_detector.detect(hashed)
                changed_records = [
                    record for record in changes if record.change_type != ChangeType.UNCHANGED
                ]
                summary = self._summary(
                    run_context=run_context,
                    status=ScanStatus.SUCCESS,
                    observations_count=len(hashed),
                    changed_count=len(changed_records),
                    sink_names=(),
                    errors=(),
                    trace_ids=trace_ids,
                )
                with trace.span("write_sinks", metadata={"changed_records": len(changed_records)}):
                    sink_results = await self.sink_router.write(
                        run_context, changed_records, summary
                    )
                if self.memory_record_builder and self.memory_router:
                    with trace.span("write_memory", metadata={"changed_records": len(changed_records)}):
                        memory_records = self.memory_record_builder.build(
                            run_context=run_context,
                            changed_records=changed_records,
                            summary=summary,
                        )
                        await self.memory_router.route(run_context, memory_records)
                final_summary = self._summary(
                    run_context=run_context,
                    status=ScanStatus.SUCCESS
                    if all(result.status == "success" for result in sink_results)
                    else ScanStatus.PARTIAL_SUCCESS,
                    observations_count=len(hashed),
                    changed_count=len(changed_records),
                    sink_names=tuple(result.sink_name for result in sink_results),
                    errors=tuple(result.error for result in sink_results if result.error),
                    trace_ids=trace_ids,
                )
            except Exception as error:
                errors.append(str(error))
                logger.exception(
                    "scan failed",
                    extra={"event": "scan_failed", "run_id": str(run_context.run_id)},
                )
                final_summary = self._summary(
                    run_context=run_context,
                    status=ScanStatus.FAILED,
                    observations_count=0,
                    changed_count=0,
                    sink_names=(),
                    errors=tuple(errors),
                    trace_ids=trace_ids,
                )
            trace.update_summary(final_summary)
        logger.info(
            "scan completed",
            extra={
                "event": "scan_complete",
                "run_id": str(final_summary.run_id),
                "status": final_summary.status.value,
                "resources_seen": final_summary.resources_seen,
                "resources_changed": final_summary.resources_changed,
                "sinks_used": list(final_summary.sinks_used),
            },
        )
        return final_summary

    def _summary(
        self,
        run_context: RunContext,
        status: ScanStatus,
        observations_count: int,
        changed_count: int,
        sink_names: tuple[str, ...],
        errors: tuple[str, ...],
        trace_ids: dict[str, str | None] | None = None,
    ) -> ScanSummary:
        return ScanSummary(
            run_id=run_context.run_id,
            correlation_id=run_context.correlation_id,
            namespace=run_context.namespace,
            status=status,
            started_at=run_context.started_at,
            finished_at=datetime.now(UTC),
            resources_seen=observations_count,
            resources_changed=changed_count,
            sinks_used=sink_names,
            trace_ids=trace_ids or {},
            errors=errors,
        )
