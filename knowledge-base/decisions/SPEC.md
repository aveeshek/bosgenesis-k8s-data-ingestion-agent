# Decision Records Specification

## Implemented decisions

- Use read-only MCP collection.
- Enforce MCP allowlists and mutation denylists in code.
- Keep mutation, remediation, alerting, anomaly detection, and MoP execution out of scope.
- Use stable hashes for deduplication.
- Keep sinks optional and independently configured.
- Support API-only, scheduler-only, and combined service runtime modes.
- Use containerd image import deployment workflow for the target cluster.
- Keep Letta disabled by default.
