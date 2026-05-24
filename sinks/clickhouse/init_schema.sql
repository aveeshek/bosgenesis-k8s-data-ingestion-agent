-- ClickHouse schema for bosgenesis-k8s-data-ingestion-agent analytical facts.
-- Default runtime identity is expected to be user "bosgenesis".

CREATE DATABASE IF NOT EXISTS bosgenesis_k8s_ingestion;

CREATE TABLE IF NOT EXISTS bosgenesis_k8s_ingestion.scan_run_facts
(
    run_id UUID,
    correlation_id String,
    namespace LowCardinality(String),
    trigger_type LowCardinality(String),
    status LowCardinality(String),
    started_at DateTime64(3, 'UTC'),
    finished_at Nullable(DateTime64(3, 'UTC')),
    duration_ms UInt64,
    resources_seen UInt32,
    resources_changed UInt32,
    helm_releases_seen UInt32,
    helm_releases_changed UInt32,
    sinks_used Array(String),
    error_count UInt32,
    trace_langfuse Nullable(String),
    trace_signoz Nullable(String),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(started_at)
ORDER BY (namespace, started_at, run_id);

CREATE TABLE IF NOT EXISTS bosgenesis_k8s_ingestion.resource_status_facts
(
    run_id UUID,
    correlation_id String,
    namespace LowCardinality(String),
    source LowCardinality(String),
    resource_kind LowCardinality(String),
    resource_name String,
    resource_uid Nullable(String),
    entity_key String,
    status_summary Nullable(String),
    content_hash String,
    changed UInt8,
    observed_at DateTime64(3, 'UTC'),
    restart_count Nullable(UInt32),
    ready_count Nullable(UInt32),
    desired_count Nullable(UInt32),
    available_count Nullable(UInt32),
    warning_event_count Nullable(UInt32),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_at)
ORDER BY (namespace, resource_kind, resource_name, observed_at, run_id);

CREATE TABLE IF NOT EXISTS bosgenesis_k8s_ingestion.helm_release_facts
(
    run_id UUID,
    correlation_id String,
    namespace LowCardinality(String),
    release_name String,
    chart_name Nullable(String),
    chart_version Nullable(String),
    app_version Nullable(String),
    revision Nullable(UInt32),
    status LowCardinality(Nullable(String)),
    entity_key String,
    content_hash String,
    changed UInt8,
    observed_at DateTime64(3, 'UTC'),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_at)
ORDER BY (namespace, release_name, observed_at, run_id);

CREATE TABLE IF NOT EXISTS bosgenesis_k8s_ingestion.change_event_facts
(
    event_id UUID,
    run_id UUID,
    correlation_id String,
    namespace LowCardinality(String),
    source LowCardinality(String),
    entity_type LowCardinality(String),
    entity_name String,
    entity_key String,
    change_type LowCardinality(String),
    previous_hash Nullable(String),
    current_hash Nullable(String),
    observed_at DateTime64(3, 'UTC'),
    event_payload String,
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(observed_at)
ORDER BY (namespace, entity_type, entity_name, observed_at, event_id);

CREATE TABLE IF NOT EXISTS bosgenesis_k8s_ingestion.sink_write_facts
(
    audit_id UUID,
    run_id Nullable(UUID),
    correlation_id Nullable(String),
    sink_name LowCardinality(String),
    operation LowCardinality(String),
    status LowCardinality(String),
    records_attempted UInt32,
    records_written UInt32,
    latency_ms UInt64,
    error_summary Nullable(String),
    inserted_at DateTime64(3, 'UTC') DEFAULT now64(3)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(inserted_at)
ORDER BY (sink_name, inserted_at, audit_id);

