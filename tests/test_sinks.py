import asyncio
from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.models import ChangeRecord, ChangeType, Observation, RunContext
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter, StdoutSink


def observation(content_hash: str) -> Observation:
    context = RunContext()
    return Observation(
        observation_id=uuid4(),
        run_id=context.run_id,
        source="k8s_mcp",
        namespace="bosgenesis",
        entity_type="Pod",
        entity_name="pod-a",
        entity_uid="uid-a",
        observed_at=context.started_at,
        status_summary="Running",
        raw_payload={},
        normalized_payload={"name": "pod-a"},
        hash_input={"name": "pod-a"},
        content_hash=content_hash,
    )


def test_stdout_sink_emits_changed_records():
    asyncio.run(_test_stdout_sink_emits_changed_records())


async def _test_stdout_sink_emits_changed_records():
    sink = StdoutSink()
    record = ChangeRecord(observation("hash-1"), ChangeType.NEW)

    result = await sink.write(RunContext(), [record])

    assert result.records_written == 1
    assert sink.emitted_lines


def test_sink_router_writes_enabled_sink():
    asyncio.run(_test_sink_router_writes_enabled_sink())


async def _test_sink_router_writes_enabled_sink():
    sink = StdoutSink()
    record = ChangeRecord(observation("hash-1"), ChangeType.NEW)
    context = RunContext()

    results = await SinkRouter([sink]).write(context, [record])

    assert results[0].sink_name == "stdout"
    assert results[0].status == "success"
