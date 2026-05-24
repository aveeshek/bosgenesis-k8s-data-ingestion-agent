import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.models import (
    ChangeRecord,
    ChangeType,
    Observation,
    RunContext,
    ScanStatus,
    ScanSummary,
)
from bosgenesis_k8s_data_ingestion_agent.memory import MemoryRecord, MemoryType
from bosgenesis_k8s_data_ingestion_agent.sinks.clickhouse import ClickHouseSink
from bosgenesis_k8s_data_ingestion_agent.sinks.postgres import PostgresSink
from bosgenesis_k8s_data_ingestion_agent.sinks.qdrant import QdrantSink
from bosgenesis_k8s_data_ingestion_agent.sinks.redis import RedisSink


def make_observation(entity_type: str = "Pod", source: str = "k8s_mcp") -> Observation:
    context = RunContext()
    normalized_payload = {
        "api_version": "v1",
        "kind": entity_type,
        "metadata": {"name": "demo", "uid": "uid-demo"},
        "status": {"phase": "Running"},
    }
    if entity_type == "HelmRelease":
        normalized_payload = {
            "release": {"name": "demo", "chart": "demo-chart", "revision": 1},
            "status": {"status": "deployed", "revision": 1},
            "history": [],
        }
    return Observation(
        observation_id=uuid4(),
        run_id=context.run_id,
        source=source,
        namespace="bosgenesis",
        entity_type=entity_type,
        entity_name="demo",
        entity_uid="uid-demo" if entity_type != "HelmRelease" else None,
        observed_at=datetime.now(UTC),
        status_summary="Running" if entity_type != "HelmRelease" else "deployed",
        raw_payload={"metadata": {"name": "demo"}},
        normalized_payload=normalized_payload,
        hash_input=normalized_payload,
        content_hash="hash-demo",
    )


def make_summary(context: RunContext) -> ScanSummary:
    return ScanSummary(
        run_id=context.run_id,
        correlation_id=context.correlation_id,
        namespace=context.namespace,
        status=ScanStatus.SUCCESS,
        started_at=context.started_at,
        finished_at=datetime.now(UTC),
        resources_seen=1,
        resources_changed=1,
    )


class FakePostgresConnection:
    def __init__(self):
        self.executed = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params):
        self.executed.append((sql, params))

    def close(self):
        self.closed = True


def test_postgres_sink_writes_snapshot_event_and_hash():
    connection = FakePostgresConnection()
    sink = PostgresSink(connection_factory=lambda: connection)
    context = RunContext()
    record = ChangeRecord(make_observation(), ChangeType.NEW)

    result = asyncio.run(sink.write(context, [record], make_summary(context)))

    assert result.records_written == 1
    assert connection.closed is True
    assert len(connection.executed) == 4
    assert "resource_snapshots" in connection.executed[1][0]
    assert "change_events" in connection.executed[2][0]
    assert "latest_entity_hashes" in connection.executed[3][0]


class FakeClickHouseClient:
    def __init__(self):
        self.inserts = []
        self.closed = False

    def insert(self, table, rows, column_names):
        self.inserts.append((table, rows, column_names))

    def close(self):
        self.closed = True


def test_clickhouse_sink_inserts_fact_rows():
    client = FakeClickHouseClient()
    sink = ClickHouseSink(client_factory=lambda: client)
    context = RunContext()
    record = ChangeRecord(make_observation(), ChangeType.NEW)

    result = asyncio.run(sink.write(context, [record], make_summary(context)))

    assert result.records_written == 1
    tables = [insert[0] for insert in client.inserts]
    assert "bosgenesis_k8s_ingestion.scan_run_facts" in tables
    assert "bosgenesis_k8s_ingestion.resource_status_facts" in tables
    assert "bosgenesis_k8s_ingestion.change_event_facts" in tables
    assert client.closed is True


class FakeQdrantClient:
    def __init__(self):
        self.upserts = []
        self.closed = False

    def upsert(self, collection_name, points):
        self.upserts.append((collection_name, points))

    def close(self):
        self.closed = True


def test_qdrant_sink_upserts_points():
    client = FakeQdrantClient()
    sink = QdrantSink(
        client_factory=lambda: client,
        vector_size=3,
        embedding_function=lambda text: [0.1, 0.2, 0.3],
    )
    context = RunContext()
    record = ChangeRecord(make_observation(), ChangeType.NEW)

    result = asyncio.run(sink.write(context, [record]))

    assert result.records_written == 1
    assert client.upserts[0][0] == "bosgenesis_k8s_observations"
    assert client.upserts[0][1][0]["vector"] == [0.1, 0.2, 0.3]
    assert client.closed is True


def test_qdrant_sink_upserts_memory_records():
    client = FakeQdrantClient()
    sink = QdrantSink(
        client_factory=lambda: client,
        vector_size=3,
        embedding_function=lambda text: [0.1, 0.2, 0.3],
    )
    context = RunContext()
    memory_record = MemoryRecord(
        memory_type=MemoryType.SEMANTIC,
        text="Pod demo is running.",
        namespace="bosgenesis",
        source="k8s_mcp",
        entity_type="Pod",
        entity_name="demo",
        entity_key="k8s_mcp:bosgenesis:Pod:demo",
        run_id=context.run_id,
        correlation_id=context.correlation_id,
        content_hash="hash-demo",
        observed_at=datetime.now(UTC),
        metadata={"status_summary": "Running"},
    )

    result = asyncio.run(sink.write_memory(context, [memory_record]))

    assert result.records_written == 1
    point = client.upserts[0][1][0]
    assert point["payload"]["memory_type"] == "semantic"
    assert point["payload"]["text"] == "Pod demo is running."


class FakeRedisClient:
    def __init__(self):
        self.set_calls = []
        self.xadd_calls = []
        self.closed = False

    async def set(self, key, value, ex=None):
        self.set_calls.append((key, value, ex))

    async def xadd(self, key, fields):
        self.xadd_calls.append((key, fields))

    async def aclose(self):
        self.closed = True


def test_redis_sink_sets_latest_hash_and_summary():
    client = FakeRedisClient()
    sink = RedisSink(client_factory=lambda: client)
    context = RunContext()
    record = ChangeRecord(make_observation(), ChangeType.NEW)

    result = asyncio.run(sink.write(context, [record], make_summary(context)))

    assert result.records_written == 1
    assert any(":latest-hash:" in call[0] for call in client.set_calls)
    assert any(call[0].endswith(":latest-run") for call in client.set_calls)
    assert client.xadd_calls[0][0] == "bg:k8s-ingestion:stream:changes"
    assert client.closed is True
