-- Runtime grants for bosgenesis-k8s-data-ingestion-agent PostgreSQL sink.
-- Execute as the schema owner or a database administrator after init_schema.sql.
-- Change "bosgenesis" below if the runtime POSTGRES_DSN uses a different user.

GRANT USAGE ON SCHEMA k8s_ingestion TO bosgenesis;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA k8s_ingestion
TO bosgenesis;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA k8s_ingestion
TO bosgenesis;

ALTER DEFAULT PRIVILEGES IN SCHEMA k8s_ingestion
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO bosgenesis;

ALTER DEFAULT PRIVILEGES IN SCHEMA k8s_ingestion
GRANT USAGE, SELECT ON SEQUENCES TO bosgenesis;
