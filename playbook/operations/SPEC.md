# Operations Playbook Specification

## Implemented status

Operational controls are available through environment variables and API endpoints.

## Implemented operations

- Inspect health through `/health`.
- Trigger scans through `/scan/run`.
- Inspect latest scan through `/scan/latest`.
- Tune scan interval with `AGENT_SCAN_INTERVAL_SECONDS`.
- Enable/disable sinks with sink-specific env vars.
- Use structured JSON logs for scan, MCP, scheduler, and sink lifecycle events.

## Future operations docs

- Sink-specific troubleshooting.
- Langfuse/SigNoz trace checks after observability exporters are implemented.
