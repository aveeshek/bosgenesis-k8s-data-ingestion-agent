# End-to-End Tests

## In-process e2e

These tests exercise the full application flow without live infrastructure:

- FastAPI request handling.
- Scan orchestrator.
- Kubernetes and Helm collectors.
- MCP client allowlist path with in-memory transports.
- Normalization.
- Stable hashing.
- Change detection and deduplication.
- Sink routing to stdout sink.

Run:

```bash
python -m pytest tests/e2e
```

## Live e2e

Live tests are intentionally opt-in because they require a deployed service and BOS Genesis cluster access.

Run only when the service is deployed:

```bash
RUN_LIVE_E2E=true \
AGENT_BASE_URL=http://data-ingestion-agent.bosgenesis.local \
python -m pytest tests/e2e -m live_e2e
```

