import asyncio

from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.entrypoints import runtime
from bosgenesis_k8s_data_ingestion_agent.entrypoints.runtime import RuntimeMode, parse_args, run_mode


class DummyOrchestrator:
    def __init__(self):
        self.requests = []

    async def run_scan(self, request):
        self.requests.append(request)
        return None


def test_parse_args_defaults_to_service():
    args = parse_args([])

    assert args.mode == "service"


def test_parse_args_accepts_api_mode():
    args = parse_args(["api"])

    assert args.mode == "api"


def test_run_mode_dispatches_api(monkeypatch):
    called = {}

    async def fake_run_api(settings, orchestrator):
        called["mode"] = "api"

    monkeypatch.setattr(runtime, "run_api", fake_run_api)

    asyncio.run(run_mode(RuntimeMode.API, Settings(), DummyOrchestrator()))

    assert called["mode"] == "api"


def test_run_mode_dispatches_scheduler(monkeypatch):
    called = {}

    async def fake_run_scheduler(settings, orchestrator):
        called["mode"] = "scheduler"

    monkeypatch.setattr(runtime, "run_scheduler", fake_run_scheduler)

    asyncio.run(run_mode(RuntimeMode.SCHEDULER, Settings(), DummyOrchestrator()))

    assert called["mode"] == "scheduler"


def test_run_mode_dispatches_service(monkeypatch):
    called = {}

    async def fake_run_service(settings, orchestrator):
        called["mode"] = "service"

    monkeypatch.setattr(runtime, "run_service", fake_run_service)

    asyncio.run(run_mode(RuntimeMode.SERVICE, Settings(), DummyOrchestrator()))

    assert called["mode"] == "service"

