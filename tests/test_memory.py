import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.memory import MemoryRecordBuilder, MemoryRouter, MemoryType
from bosgenesis_k8s_data_ingestion_agent.models import (
    ChangeRecord,
    ChangeType,
    Observation,
    RunContext,
    ScanStatus,
    ScanSummary,
    SinkResult,
)


def make_observation() -> Observation:
    context = RunContext()
    return Observation(
        observation_id=uuid4(),
        run_id=context.run_id,
        source="k8s_mcp",
        namespace="bosgenesis",
        entity_type="Pod",
        entity_name="demo-pod",
        entity_uid="uid-demo",
        observed_at=datetime.now(UTC),
        status_summary="Running",
        raw_payload={},
        normalized_payload={"metadata": {"name": "demo-pod"}, "status": {"phase": "Running"}},
        hash_input={"metadata": {"name": "demo-pod"}, "status": {"phase": "Running"}},
        content_hash="hash-demo",
    )


def make_summary(context: RunContext) -> ScanSummary:
    return ScanSummary(
        run_id=context.run_id,
        correlation_id=context.correlation_id,
        namespace=context.namespace,
        status=ScanStatus.SUCCESS,
        started_at=context.started_at,
        finished_at=datetime.now(UTC),
        resources_seen=1,
        resources_changed=1,
        sinks_used=("stdout",),
    )


def test_memory_record_builder_creates_session_episodic_and_semantic_records():
    context = RunContext()
    change_record = ChangeRecord(make_observation(), ChangeType.NEW)

    records = MemoryRecordBuilder().build(context, [change_record], make_summary(context))

    assert [record.memory_type for record in records] == [
        MemoryType.SESSION,
        MemoryType.EPISODIC,
        MemoryType.SEMANTIC,
    ]
    assert records[0].entity_type == "ScanRun"
    assert records[1].metadata["change_type"] == "new"
    assert records[2].metadata["status_summary"] == "Running"


class FakeMemorySink:
    name = "fake-memory"
    enabled = True

    def __init__(self):
        self.records = []

    async def write_memory(self, run_context, memory_records):
        self.records.extend(memory_records)
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(memory_records),
            records_written=len(memory_records),
            latency_ms=0,
        )


def test_memory_router_routes_enabled_memory_types():
    context = RunContext()
    sink = FakeMemorySink()
    change_record = ChangeRecord(make_observation(), ChangeType.NEW)
    records = MemoryRecordBuilder().build(context, [change_record], make_summary(context))

    results = asyncio.run(MemoryRouter([sink], enabled_types=frozenset({MemoryType.SEMANTIC})).route(context, records))

    assert results[0].records_written == 1
    assert len(sink.records) == 1
    assert sink.records[0].memory_type == MemoryType.SEMANTIC

