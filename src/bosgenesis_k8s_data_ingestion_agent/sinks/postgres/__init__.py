"""PostgreSQL sink writer."""

from __future__ import annotations

import asyncio
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


ConnectionFactory = Callable[[], Any]


@dataclass
class PostgresSink:
    dsn: str | None = None
    enabled: bool = True
    connection_factory: ConnectionFactory | None = None
    schema: str = "k8s_ingestion"
    name: str = "postgres"

    async def write(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None = None,
    ) -> SinkResult:
        started = time.perf_counter()
        written = await asyncio.to_thread(self._write_sync, run_context, records, summary)
        return SinkResult(
            sink_name=self.name,
            status="success",
            records_attempted=len(records),
            records_written=written,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _connect(self):
        if self.connection_factory:
            return self.connection_factory()
        if not self.dsn:
            raise ValueError("PostgresSink requires dsn or connection_factory")
        import psycopg

        return psycopg.connect(self.dsn)

    def _write_sync(
        self,
        run_context: RunContext,
        records: list[ChangeRecord],
        summary: ScanSummary | None,
    ) -> int:
        conn = self._connect()
        written = 0
        try:
            with conn:
                if summary:
                    self._insert_summary(conn, summary)
                for record in records:
                    if is_helm_observation(record.observation):
                        self._insert_helm_snapshot(conn, run_context, record)
                    else:
                        self._insert_resource_snapshot(conn, run_context, record)
                    self._insert_change_event(conn, run_context, record)
                    self._upsert_latest_hash(conn, run_context, record)
                    written += 1
        finally:
            close = getattr(conn, "close", None)
            if callable(close):
                close()
        return written

    def _insert_summary(self, conn, summary: ScanSummary) -> None:
        conn.execute(
            f"""
            INSERT INTO {self.schema}.scan_runs (
                run_id, correlation_id, namespace, trigger_type, status,
                started_at, finished_at, resources_seen, resources_changed,
                helm_releases_seen, helm_releases_changed, sinks_used, trace_ids, error_summary
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
            ON CONFLICT (run_id) DO NOTHING
            """,
            (
                summary.run_id,
                summary.correlation_id,
                summary.namespace,
                "unknown",
                summary.status.value,
                summary.started_at,
                summary.finished_at,
                summary.resources_seen,
                summary.resources_changed,
                summary.helm_releases_seen,
                summary.helm_releases_changed,
                list(summary.sinks_used),
                json_dumps(summary.trace_ids),
                json_dumps({"errors": list(summary.errors)}) if summary.errors else None,
            ),
        )

    def _insert_resource_snapshot(
        self, conn, run_context: RunContext, record: ChangeRecord
    ) -> None:
        observation = record.observation
        conn.execute(
            f"""
            INSERT INTO {self.schema}.resource_snapshots (
                snapshot_id, run_id, correlation_id, namespace, source, api_version,
                resource_kind, resource_name, resource_uid, entity_key, status_summary,
                content_hash, observed_at, normalized_payload, raw_payload
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
            """,
            (
                observation.observation_id,
                run_context.run_id,
                run_context.correlation_id,
                observation.namespace,
                observation.source,
                observation.normalized_payload.get("api_version"),
                observation.entity_type,
                observation.entity_name,
                observation.entity_uid,
                observation.entity_key,
                observation.status_summary,
                observation.content_hash,
                observation.observed_at,
                json_dumps(observation.normalized_payload),
                json_dumps(observation.raw_payload),
            ),
        )

    def _insert_helm_snapshot(self, conn, run_context: RunContext, record: ChangeRecord) -> None:
        observation = record.observation
        release = observation.normalized_payload.get("release", {})
        status = observation.normalized_payload.get("status", {})
        conn.execute(
            f"""
            INSERT INTO {self.schema}.helm_release_snapshots (
                snapshot_id, run_id, correlation_id, namespace, source, release_name,
                chart_name, chart_version, app_version, revision, status, entity_key,
                content_hash, observed_at, normalized_payload, raw_payload
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s::jsonb)
            """,
            (
                observation.observation_id,
                run_context.run_id,
                run_context.correlation_id,
                observation.namespace,
                observation.source,
                observation.entity_name,
                release.get("chart") or release.get("chart_name"),
                release.get("chart_version"),
                release.get("app_version"),
                status.get("revision") or release.get("revision"),
                observation.status_summary,
                observation.entity_key,
                observation.content_hash,
                observation.observed_at,
                json_dumps(observation.normalized_payload),
                json_dumps(observation.raw_payload),
            ),
        )

    def _insert_change_event(self, conn, run_context: RunContext, record: ChangeRecord) -> None:
        observation = record.observation
        conn.execute(
            f"""
            INSERT INTO {self.schema}.change_events (
                event_id, run_id, correlation_id, namespace, source, entity_type,
                entity_name, entity_key, change_type, previous_hash, current_hash,
                observed_at, event_payload
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
            """,
            (
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
            ),
        )

    def _upsert_latest_hash(self, conn, run_context: RunContext, record: ChangeRecord) -> None:
        observation = record.observation
        conn.execute(
            f"""
            INSERT INTO {self.schema}.latest_entity_hashes (
                namespace, source, entity_type, entity_name, entity_key,
                latest_hash, latest_run_id, latest_observed_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (namespace, source, entity_key)
            DO UPDATE SET
                latest_hash = EXCLUDED.latest_hash,
                latest_run_id = EXCLUDED.latest_run_id,
                latest_observed_at = EXCLUDED.latest_observed_at
            """,
            (
                observation.namespace,
                observation.source,
                observation.entity_type,
                observation.entity_name,
                observation.entity_key,
                observation.content_hash,
                run_context.run_id,
                observation.observed_at,
            ),
        )
