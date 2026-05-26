import asyncio

from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector, InMemoryHashStateStore
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.models import ScanRequest, ScanStatus
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter, StdoutSink


class DummySpan:
    def __init__(self, tracer, name):
        self.tracer = tracer
        self.name = name

    def __enter__(self):
        self.tracer.spans.append(self.name)

    def __exit__(self, exc_type, exc, traceback):
        return None


class DummyTrace:
    trace_id = "langfuse-trace-1"

    def __init__(self):
        self.spans = []
        self.summary = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return None

    def span(self, name, *, input=None, metadata=None):
        _ = input, metadata
        return DummySpan(self, name)

    def update_summary(self, summary):
        self.summary = summary


class DummyTracer:
    def __init__(self):
        self.trace = DummyTrace()

    def scan(self, request, run_context):
        _ = request, run_context
        return self.trace


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


def test_orchestrator_adds_langfuse_trace_id():
    asyncio.run(_test_orchestrator_adds_langfuse_trace_id())


async def _test_orchestrator_adds_langfuse_trace_id():
    tracer = DummyTracer()
    orchestrator = ScanOrchestrator(
        change_detector=ChangeDetector(InMemoryHashStateStore()),
        sink_router=SinkRouter([StdoutSink()]),
        langfuse_tracer=tracer,
    )

    summary = await orchestrator.run_scan(ScanRequest())

    assert summary.trace_ids["langfuse"] == "langfuse-trace-1"
    assert tracer.trace.summary == summary
    assert "normalize" in tracer.trace.spans
    assert "write_sinks" in tracer.trace.spans
