import asyncio

from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector, InMemoryHashStateStore
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.models import ScanRequest, ScanStatus
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter, StdoutSink


def test_orchestrator_runs_without_collectors():
    asyncio.run(_test_orchestrator_runs_without_collectors())


async def _test_orchestrator_runs_without_collectors():
    orchestrator = ScanOrchestrator(
        change_detector=ChangeDetector(InMemoryHashStateStore()),
        sink_router=SinkRouter([StdoutSink()]),
    )

    summary = await orchestrator.run_scan(ScanRequest())

    assert summary.status == ScanStatus.SUCCESS
    assert summary.resources_seen == 0
    assert summary.sinks_used == ("stdout",)
