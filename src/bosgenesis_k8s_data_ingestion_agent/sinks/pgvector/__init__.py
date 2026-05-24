"""pgvector sink placeholder."""

from bosgenesis_k8s_data_ingestion_agent.sinks.base import DisabledSink


class PgvectorSink(DisabledSink):
    def __init__(self, enabled: bool = False):
        super().__init__(name="pgvector", enabled=enabled)

