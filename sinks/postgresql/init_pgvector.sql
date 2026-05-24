-- Optional pgvector initialization for semantic memory records.
-- Run this only when the PostgreSQL instance has the vector extension installed.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS k8s_ingestion;

CREATE TABLE IF NOT EXISTS k8s_ingestion.memory_vectors (
    memory_id UUID PRIMARY KEY,
    run_id UUID,
    correlation_id TEXT,
    namespace TEXT NOT NULL DEFAULT 'bosgenesis',
    source TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    summary TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    embedding vector(1536),
    observed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_memory_vectors_entity
    ON k8s_ingestion.memory_vectors(namespace, entity_key, observed_at DESC);

CREATE INDEX IF NOT EXISTS idx_memory_vectors_metadata_gin
    ON k8s_ingestion.memory_vectors USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_memory_vectors_embedding_cosine
    ON k8s_ingestion.memory_vectors
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

