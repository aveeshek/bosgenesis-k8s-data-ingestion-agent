-- PostgreSQL schema for bosgenesis-k8s-data-ingestion-agent.
-- Default runtime identity is expected to be user "bosgenesis".
-- Execute with a database user that can create schemas, tables, indexes, and triggers.

CREATE SCHEMA IF NOT EXISTS k8s_ingestion;

CREATE TABLE IF NOT EXISTS k8s_ingestion.scan_runs (
    run_id UUID PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    trigger_type TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    duration_ms BIGINT,
    resources_seen INTEGER NOT NULL DEFAULT 0,
    resources_changed INTEGER NOT NULL DEFAULT 0,
    helm_releases_seen INTEGER NOT NULL DEFAULT 0,
    helm_releases_changed INTEGER NOT NULL DEFAULT 0,
    sinks_used TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    trace_ids JSONB NOT NULL DEFAULT '{}'::JSONB,
    error_summary JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS k8s_ingestion.resource_snapshots (
    snapshot_id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES k8s_ingestion.scan_runs(run_id) ON DELETE CASCADE,
    correlation_id TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    source TEXT NOT NULL DEFAULT 'k8s_mcp',
    api_version TEXT,
    resource_kind TEXT NOT NULL,
    resource_name TEXT NOT NULL,
    resource_uid TEXT,
    entity_key TEXT NOT NULL,
    status_summary TEXT,
    content_hash TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    normalized_payload JSONB NOT NULL,
    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS k8s_ingestion.helm_release_snapshots (
    snapshot_id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES k8s_ingestion.scan_runs(run_id) ON DELETE CASCADE,
    correlation_id TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    source TEXT NOT NULL DEFAULT 'helm_mcp',
    release_name TEXT NOT NULL,
    chart_name TEXT,
    chart_version TEXT,
    app_version TEXT,
    revision INTEGER,
    status TEXT,
    entity_key TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    normalized_payload JSONB NOT NULL,
    raw_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS k8s_ingestion.change_events (
    event_id UUID PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES k8s_ingestion.scan_runs(run_id) ON DELETE CASCADE,
    correlation_id TEXT NOT NULL,
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    source TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    change_type TEXT NOT NULL,
    previous_hash TEXT,
    current_hash TEXT,
    observed_at TIMESTAMPTZ NOT NULL,
    event_payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS k8s_ingestion.latest_entity_hashes (
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    source TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    latest_hash TEXT NOT NULL,
    latest_run_id UUID NOT NULL,
    latest_observed_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (namespace, source, entity_key)
);

CREATE TABLE IF NOT EXISTS k8s_ingestion.sink_write_audit (
    audit_id UUID PRIMARY KEY,
    run_id UUID,
    correlation_id TEXT,
    sink_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    records_attempted INTEGER NOT NULL DEFAULT 0,
    records_written INTEGER NOT NULL DEFAULT 0,
    latency_ms BIGINT,
    error_summary JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scan_runs_namespace_started
    ON k8s_ingestion.scan_runs(namespace, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_resource_snapshots_entity_observed
    ON k8s_ingestion.resource_snapshots(namespace, entity_key, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_resource_snapshots_kind_name
    ON k8s_ingestion.resource_snapshots(namespace, resource_kind, resource_name);

CREATE INDEX IF NOT EXISTS idx_resource_snapshots_hash
    ON k8s_ingestion.resource_snapshots(content_hash);

CREATE INDEX IF NOT EXISTS idx_resource_snapshots_payload_gin
    ON k8s_ingestion.resource_snapshots USING GIN (normalized_payload);

CREATE INDEX IF NOT EXISTS idx_helm_snapshots_entity_observed
    ON k8s_ingestion.helm_release_snapshots(namespace, entity_key, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_helm_snapshots_release
    ON k8s_ingestion.helm_release_snapshots(namespace, release_name);

CREATE INDEX IF NOT EXISTS idx_helm_snapshots_hash
    ON k8s_ingestion.helm_release_snapshots(content_hash);

CREATE INDEX IF NOT EXISTS idx_change_events_entity_observed
    ON k8s_ingestion.change_events(namespace, entity_key, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_change_events_type_observed
    ON k8s_ingestion.change_events(change_type, observed_at DESC);

CREATE OR REPLACE FUNCTION k8s_ingestion.touch_latest_entity_hashes()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_latest_entity_hashes_updated_at
    ON k8s_ingestion.latest_entity_hashes;

CREATE TRIGGER trg_latest_entity_hashes_updated_at
BEFORE UPDATE ON k8s_ingestion.latest_entity_hashes
FOR EACH ROW
EXECUTE FUNCTION k8s_ingestion.touch_latest_entity_hashes();

