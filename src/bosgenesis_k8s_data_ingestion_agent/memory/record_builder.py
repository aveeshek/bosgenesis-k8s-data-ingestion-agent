"""Build compact agentic memory records from scan output."""

from __future__ import annotations

from dataclasses import dataclass

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, RunContext, ScanSummary
from bosgenesis_k8s_data_ingestion_agent.sinks.serialization import to_jsonable
from bosgenesis_k8s_data_ingestion_agent.memory.records import MemoryRecord, MemoryType


@dataclass(frozen=True)
class MemoryRecordBuilder:
    include_session_records: bool = True
    include_episodic_records: bool = True
    include_semantic_records: bool = True

    def build(
        self,
        run_context: RunContext,
        changed_records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> list[MemoryRecord]:
        records: list[MemoryRecord] = []
        if self.include_session_records and summary:
            records.append(self.build_session_record(run_context, summary))
        for change_record in changed_records:
            if self.include_episodic_records:
                records.append(self.build_episodic_record(run_context, change_record))
            if self.include_semantic_records:
                records.append(self.build_semantic_record(run_context, change_record))
        return records

    def build_session_record(self, run_context: RunContext, summary: ScanSummary) -> MemoryRecord:
        text = (
            f"Scan {summary.run_id} completed with status {summary.status.value}; "
            f"resources_seen={summary.resources_seen}, "
            f"resources_changed={summary.resources_changed}, "
            f"sinks_used={','.join(summary.sinks_used) or 'none'}."
        )
        return MemoryRecord(
            memory_type=MemoryType.SESSION,
            text=text,
            namespace=summary.namespace,
            source="agent_scan",
            entity_type="ScanRun",
            entity_name=str(summary.run_id),
            entity_key=f"agent_scan:{summary.namespace}:ScanRun:{summary.run_id}",
            run_id=summary.run_id,
            correlation_id=summary.correlation_id,
            observed_at=summary.finished_at,
            metadata={
                "trigger_type": run_context.trigger_type,
                "status": summary.status.value,
                "resources_seen": summary.resources_seen,
                "resources_changed": summary.resources_changed,
                "helm_releases_seen": summary.helm_releases_seen,
                "helm_releases_changed": summary.helm_releases_changed,
                "sinks_used": list(summary.sinks_used),
                "errors": list(summary.errors),
            },
        )

    def build_episodic_record(
        self, run_context: RunContext, change_record: ChangeRecord
    ) -> MemoryRecord:
        observation = change_record.observation
        text = (
            f"During scan {run_context.run_id}, {observation.entity_type} "
            f"{observation.entity_name} in namespace {observation.namespace} was "
            f"marked {change_record.change_type.value}."
        )
        return MemoryRecord(
            memory_type=MemoryType.EPISODIC,
            text=text,
            namespace=observation.namespace,
            source=observation.source,
            entity_type=observation.entity_type,
            entity_name=observation.entity_name,
            entity_key=observation.entity_key,
            run_id=run_context.run_id,
            correlation_id=run_context.correlation_id,
            content_hash=observation.content_hash,
            observed_at=observation.observed_at,
            metadata={
                "change_type": change_record.change_type.value,
                "previous_hash": change_record.previous_hash,
                "current_hash": observation.content_hash,
            },
        )

    def build_semantic_record(
        self, run_context: RunContext, change_record: ChangeRecord
    ) -> MemoryRecord:
        observation = change_record.observation
        text = (
            f"{observation.entity_type} {observation.entity_name} in namespace "
            f"{observation.namespace} has status {observation.status_summary or 'unknown'} "
            f"and change type {change_record.change_type.value}."
        )
        return MemoryRecord(
            memory_type=MemoryType.SEMANTIC,
            text=text,
            namespace=observation.namespace,
            source=observation.source,
            entity_type=observation.entity_type,
            entity_name=observation.entity_name,
            entity_key=observation.entity_key,
            run_id=run_context.run_id,
            correlation_id=run_context.correlation_id,
            content_hash=observation.content_hash,
            observed_at=observation.observed_at,
            metadata={
                "status_summary": observation.status_summary,
                "change_type": change_record.change_type.value,
                "normalized_payload": to_jsonable(observation.normalized_payload),
            },
        )

