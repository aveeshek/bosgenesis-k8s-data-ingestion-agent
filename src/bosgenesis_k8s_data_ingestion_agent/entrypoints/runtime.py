"""Runtime mode selection for API, scheduler, and combined service modes."""

from __future__ import annotations

import argparse
import asyncio
from enum import StrEnum

from bosgenesis_k8s_data_ingestion_agent.api import create_app
from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.observability import get_logger
from bosgenesis_k8s_data_ingestion_agent.scheduler import Scheduler


class RuntimeMode(StrEnum):
    API = "api"
    SCHEDULER = "scheduler"
    SERVICE = "service"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bosgenesis-k8s-data-ingestion-agent",
        description="Run the BOS Genesis K8s data ingestion agent.",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=[mode.value for mode in RuntimeMode],
        default=RuntimeMode.SERVICE.value,
        help="Runtime mode: api, scheduler, or service. Defaults to service.",
    )
    return parser.parse_args(argv)


async def run_api(settings: Settings, orchestrator: ScanOrchestrator) -> None:
    import uvicorn

    logger = get_logger(__name__)
    logger.info(
        "api runtime starting",
        extra={
            "event": "runtime_api_start",
            "host": settings.api.host,
            "port": settings.api.port,
        },
    )
    config = uvicorn.Config(
        create_app(settings, orchestrator),
        host=settings.api.host,
        port=settings.api.port,
        log_config=None,
    )
    await uvicorn.Server(config).serve()


async def run_scheduler(settings: Settings, orchestrator: ScanOrchestrator) -> None:
    logger = get_logger(__name__)
    logger.info(
        "scheduler runtime starting",
        extra={
            "event": "runtime_scheduler_start",
            "namespace": settings.agent.namespace,
            "scan_interval_seconds": settings.agent.scan_interval_seconds,
            "run_on_startup": settings.agent.run_on_startup,
        },
    )
    scheduler = Scheduler(
        orchestrator=orchestrator,
        scan_interval_seconds=settings.agent.scan_interval_seconds,
        namespace=settings.agent.namespace,
        run_on_startup=settings.agent.run_on_startup,
    )
    await scheduler.run_forever()


async def run_service(settings: Settings, orchestrator: ScanOrchestrator) -> None:
    logger = get_logger(__name__)
    logger.info("service runtime starting", extra={"event": "runtime_service_start"})
    await asyncio.gather(
        run_api(settings, orchestrator),
        run_scheduler(settings, orchestrator),
    )


async def run_mode(
    mode: RuntimeMode,
    settings: Settings,
    orchestrator: ScanOrchestrator,
) -> None:
    if mode == RuntimeMode.API:
        await run_api(settings, orchestrator)
    elif mode == RuntimeMode.SCHEDULER:
        await run_scheduler(settings, orchestrator)
    elif mode == RuntimeMode.SERVICE:
        await run_service(settings, orchestrator)
    else:  # pragma: no cover - argparse prevents this path
        raise ValueError(f"unsupported runtime mode: {mode}")

