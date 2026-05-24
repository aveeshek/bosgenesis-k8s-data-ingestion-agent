import asyncio

from bosgenesis_k8s_data_ingestion_agent.scheduler import Scheduler


class StopAfterFirstRunOrchestrator:
    def __init__(self):
        self.requests = []
        self.scheduler = None

    async def run_scan(self, request):
        self.requests.append(request)
        self.scheduler.stop()


def test_scheduler_can_run_startup_scan_and_stop():
    orchestrator = StopAfterFirstRunOrchestrator()
    scheduler = Scheduler(
        orchestrator=orchestrator,
        scan_interval_seconds=3600,
        namespace="bosgenesis",
        run_on_startup=True,
    )
    orchestrator.scheduler = scheduler

    asyncio.run(scheduler.run_forever())

    assert len(orchestrator.requests) == 1
    assert orchestrator.requests[0].trigger_type == "startup"

