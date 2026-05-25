"""Command-line entrypoint."""

from __future__ import annotations

import asyncio

from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector, InMemoryHashStateStore
from bosgenesis_k8s_data_ingestion_agent.collectors import HelmCollector, KubernetesCollector
from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.core import ScanOrchestrator
from bosgenesis_k8s_data_ingestion_agent.entrypoints.runtime import RuntimeMode, parse_args, run_mode
from bosgenesis_k8s_data_ingestion_agent.mcp_clients import (
    HelmManagerClient,
    K8sInspectorClient,
    StreamableHttpMcpTransport,
)
from bosgenesis_k8s_data_ingestion_agent.memory import MemoryRecordBuilder, MemoryRouter
from bosgenesis_k8s_data_ingestion_agent.observability import configure_logging
from bosgenesis_k8s_data_ingestion_agent.sinks import SinkRouter, StdoutSink
from bosgenesis_k8s_data_ingestion_agent.sinks.clickhouse import ClickHouseSink
from bosgenesis_k8s_data_ingestion_agent.sinks.postgres import PostgresSink
from bosgenesis_k8s_data_ingestion_agent.sinks.qdrant import QdrantSink
from bosgenesis_k8s_data_ingestion_agent.sinks.redis import RedisSink


def build_orchestrator(settings: Settings) -> ScanOrchestrator:
    k8s_collector = None
    helm_collector = None
    if settings.k8s_mcp.enabled:
        k8s_transport = StreamableHttpMcpTransport(
            timeout_seconds=settings.k8s_mcp.timeout_seconds,
            host_header=settings.k8s_mcp.host_header,
        )
        k8s_collector = KubernetesCollector(
            K8sInspectorClient(settings.k8s_mcp.url, k8s_transport)
        )
    if settings.helm_mcp.enabled:
        helm_transport = StreamableHttpMcpTransport(
            timeout_seconds=settings.helm_mcp.timeout_seconds,
            host_header=settings.helm_mcp.host_header,
        )
        helm_collector = HelmCollector(
            HelmManagerClient(settings.helm_mcp.url, helm_transport)
        )
    sinks = [
        PostgresSink(
            dsn=settings.sinks.postgres_dsn,
            enabled=settings.sinks.postgres_enabled,
        ),
        ClickHouseSink(
            host=settings.sinks.clickhouse_host,
            port=settings.sinks.clickhouse_port,
            username=settings.sinks.clickhouse_user,
            password=settings.sinks.clickhouse_password,
            database=settings.sinks.clickhouse_database,
            enabled=settings.sinks.clickhouse_enabled,
        ),
        QdrantSink(
            url=settings.sinks.qdrant_url,
            api_key=settings.sinks.qdrant_api_key,
            collection_name=settings.sinks.qdrant_collection,
            vector_size=settings.sinks.qdrant_vector_size,
            enabled=settings.sinks.qdrant_enabled,
        ),
        RedisSink(
            host=settings.sinks.redis_host,
            port=settings.sinks.redis_port,
            db=settings.sinks.redis_db,
            password=settings.sinks.redis_password,
            key_prefix=settings.sinks.redis_key_prefix,
            enabled=settings.sinks.redis_enabled,
        ),
        StdoutSink(enabled=settings.sinks.stdout_enabled),
    ]
    memory_sinks = [sink for sink in sinks if hasattr(sink, "write_memory")]
    return ScanOrchestrator(
        change_detector=ChangeDetector(store=InMemoryHashStateStore()),
        sink_router=SinkRouter(
            sinks=sinks,
            strict=settings.agent.strict_sinks,
        ),
        k8s_collector=k8s_collector,
        helm_collector=helm_collector,
        memory_record_builder=MemoryRecordBuilder(),
        memory_router=MemoryRouter(memory_sinks) if memory_sinks else None,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    settings = Settings.from_env()
    configure_logging(settings.observability.log_level, settings.observability.service_name)
    orchestrator = build_orchestrator(settings)
    asyncio.run(run_mode(RuntimeMode(args.mode), settings, orchestrator))
