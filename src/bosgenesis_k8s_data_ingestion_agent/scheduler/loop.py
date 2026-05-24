"""Async scheduler loop."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.models import ScanRequest
from bosgenesis_k8s_data_ingestion_agent.observability import get_logger


@dataclass
class Scheduler:
    orchestrator: ScanOrchestrator
    scan_interval_seconds: int
    namespace: str = "bosgenesis"
    run_on_startup: bool = False
    _running: bool = False

    async def run_forever(self) -> None:
        self._running = True
        logger = get_logger(__name__)
        if self.run_on_startup:
            logger.info(
                "scheduled startup scan",
                extra={"event": "scheduler_startup_scan", "namespace": self.namespace},
            )
            await self.orchestrator.run_scan(
                ScanRequest(trigger_type="startup", namespace=self.namespace)
            )
        while self._running:
            logger.info("scheduled scan tick", extra={"event": "scheduler_tick"})
            await self.orchestrator.run_scan(
                ScanRequest(trigger_type="scheduled", namespace=self.namespace)
            )
            await asyncio.sleep(self.scan_interval_seconds)

    def stop(self) -> None:
        self._running = False
