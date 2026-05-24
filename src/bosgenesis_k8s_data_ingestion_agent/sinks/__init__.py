"""Sink interfaces and routers."""

from bosgenesis_k8s_data_ingestion_agent.sinks.base import BaseSink, DisabledSink
from bosgenesis_k8s_data_ingestion_agent.sinks.clickhouse import ClickHouseSink
from bosgenesis_k8s_data_ingestion_agent.sinks.postgres import PostgresSink
from bosgenesis_k8s_data_ingestion_agent.sinks.qdrant import QdrantSink
from bosgenesis_k8s_data_ingestion_agent.sinks.redis import RedisSink
from bosgenesis_k8s_data_ingestion_agent.sinks.router import SinkRouter
from bosgenesis_k8s_data_ingestion_agent.sinks.stdout import StdoutSink

__all__ = [
    "BaseSink",
    "ClickHouseSink",
    "DisabledSink",
    "PostgresSink",
    "QdrantSink",
    "RedisSink",
    "SinkRouter",
    "StdoutSink",
]
