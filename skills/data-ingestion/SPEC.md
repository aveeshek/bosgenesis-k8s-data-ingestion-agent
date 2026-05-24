# Data Ingestion Skill Specification

## Implemented status

No skill runtime is implemented yet.

## Available invocation path

Agents can call:

```text
POST /scan/run
```

## Responsibilities for future skill

- Call the on-demand scan endpoint.
- Request bounded logs only when needed.
- Preserve run and correlation IDs.
- Avoid requesting Kubernetes or Helm mutation.
