"""ClickHouse analytical sink writer."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Callable
from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.models import (
    ChangeRecord,
    RunContext,
    ScanSummary,
    SinkResult,
)
from bosgenesis_k8s_data_ingestion_agent.sinks.serialization import (
    is_helm_observation,
    json_dumps,
)


ClientFactory = Callable[[], Any]


@dataclass
class ClickHouseSink:
    host: str = "clickhouse.bosgenesis.svc.cluster.local"
    port: int = 8123
    username: str = "bosgenesis"
    password: str | None = None
    database: str = "bosgenesis_k8s_ingestion"
    enabled: bool = True
    client_factory: ClientFactory | None = None
    name: str = "clickhouse"

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        started = time.perf_counter()
        client = self._client()
        written = 0
        if summary:
            client.insert(
                f"{self.database}.scan_run_facts",
                [self._summary_row(summary)],
                column_names=SCAN_RUN_COLUMNS,
            )
        resource_rows = [self._resource_row(record, run_context) for record in records if not is_helm_observation(record.observation)]
        helm_rows = [self._helm_row(record, run_context) for record in records if is_helm_observation(record.observation)]
        event_rows = [self._event_row(record, run_context) for record in records]
        if resource_rows:
            client.insert(
                f"{self.database}.resource_status_facts",
                resource_rows,
                column_names=RESOURCE_COLUMNS,
            )
            written += len(resource_rows)
        if helm_rows:
            client.insert(
                f"{self.database}.helm_release_facts",
                helm_rows,
                column_names=HELM_COLUMNS,
            )
            written += len(helm_rows)
        if event_rows:
            client.insert(
                f"{self.database}.change_event_facts",
                event_rows,
                column_names=EVENT_COLUMNS,
            )
        close = getattr(client, "close", None)
        if callable(close):
            close()
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(records),
            records_written=written,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _client(self):
        if self.client_factory:
            return self.client_factory()
        import clickhouse_connect

        kwargs = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "database": self.database,
        }
        if self.password is not None:
            kwargs["password"] = self.password
        return clickhouse_connect.get_client(**kwargs)

    def _summary_row(self, summary: ScanSummary) -> tuple:
        return (
            summary.run_id,
            summary.correlation_id,
            summary.namespace,
            "unknown",
            summary.status.value,
            summary.started_at,
            summary.finished_at,
            0,
            summary.resources_seen,
            summary.resources_changed,
            summary.helm_releases_seen,
            summary.helm_releases_changed,
            list(summary.sinks_used),
            len(summary.errors),
            summary.trace_ids.get("langfuse"),
            summary.trace_ids.get("signoz"),
        )

    def _resource_row(self, record: ChangeRecord, run_context: RunContext) -> tuple:
        observation = record.observation
        status = observation.normalized_payload.get("status", {})
        return (
            run_context.run_id,
            run_context.correlation_id,
            observation.namespace,
            observation.source,
            observation.entity_type,
            observation.entity_name,
            observation.entity_uid,
            observation.entity_key,
            observation.status_summary,
            observation.content_hash or "",
            1,
            observation.observed_at,
            _optional_int(status.get("restartCount") or status.get("restart_count")),
            _optional_int(status.get("readyReplicas") or status.get("ready_count")),
            _optional_int(status.get("replicas") or status.get("desired_count")),
            _optional_int(status.get("availableReplicas") or status.get("available_count")),
            None,
        )

    def _helm_row(self, record: ChangeRecord, run_context: RunContext) -> tuple:
        observation = record.observation
        release = observation.normalized_payload.get("release", {})
        status = observation.normalized_payload.get("status", {})
        return (
            run_context.run_id,
            run_context.correlation_id,
            observation.namespace,
            observation.entity_name,
            release.get("chart") or release.get("chart_name"),
            release.get("chart_version"),
            release.get("app_version"),
            _optional_int(status.get("revision") or release.get("revision")),
            observation.status_summary,
            observation.entity_key,
            observation.content_hash or "",
            1,
            observation.observed_at,
        )

    def _event_row(self, record: ChangeRecord, run_context: RunContext) -> tuple:
        observation = record.observation
        return (
            uuid4(),
            run_context.run_id,
            run_context.correlation_id,
            observation.namespace,
            observation.source,
            observation.entity_type,
            observation.entity_name,
            observation.entity_key,
            record.change_type.value,
            record.previous_hash,
            observation.content_hash,
            observation.observed_at,
            json_dumps({"status_summary": observation.status_summary}),
        )


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


SCAN_RUN_COLUMNS = [
    "run_id",
    "correlation_id",
    "namespace",
    "trigger_type",
    "status",
    "started_at",
    "finished_at",
    "duration_ms",
    "resources_seen",
    "resources_changed",
    "helm_releases_seen",
    "helm_releases_changed",
    "sinks_used",
    "error_count",
    "trace_langfuse",
    "trace_signoz",
]

RESOURCE_COLUMNS = [
    "run_id",
    "correlation_id",
    "namespace",
    "source",
    "resource_kind",
    "resource_name",
    "resource_uid",
    "entity_key",
    "status_summary",
    "content_hash",
    "changed",
    "observed_at",
    "restart_count",
    "ready_count",
    "desired_count",
    "available_count",
    "warning_event_count",
]

HELM_COLUMNS = [
    "run_id",
    "correlation_id",
    "namespace",
    "release_name",
    "chart_name",
    "chart_version",
    "app_version",
    "revision",
    "status",
    "entity_key",
    "content_hash",
    "changed",
    "observed_at",
]

EVENT_COLUMNS = [
    "event_id",
    "run_id",
    "correlation_id",
    "namespace",
    "source",
    "entity_type",
    "entity_name",
    "entity_key",
    "change_type",
    "previous_hash",
    "current_hash",
    "observed_at",
    "event_payload",
]
