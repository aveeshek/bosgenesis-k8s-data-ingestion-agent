# Project Structure Specification

## Intent

The repository is organized around independently testable modules: invocation, orchestration, MCP clients, collectors, normalization, hashing, change detection, sinks, observability, deployment, Helm packaging, memory, playbooks, and skills.

## Top-level layout

- `src/`: future Python package modules.
- `config/`: non-secret configuration specifications.
- `deploy/`: Kubernetes deployment specification structure.
- `charts/`: Helm chart specification structure.
- `sinks/`: datastore initialization assets for PostgreSQL, ClickHouse, Qdrant, and Redis.
- `tests/`: future test strategy and contract specifications.
- `docs/`: generated or curated project documentation.
- `codex/`: Codex project guidance, prompts, and local workflow specs.
- `knowledge-base/`: architecture, design, schema, and session knowledge.
- `memory/`: agent memory strategy and sink contracts.
- `playbook/`: operational playbooks and validation plans.
- `skills/`: future Codex or agent skill definitions.

## No-code constraint

All files in this initial scaffold are Markdown specifications. No executable source, Helm templates, Kubernetes manifests, scripts, dependency manifests, or runtime configuration files are included yet.
