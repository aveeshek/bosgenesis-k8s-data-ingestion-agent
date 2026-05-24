# Codex Config Specification

## Implemented status

No Codex-local config files are implemented yet.

## Current validation commands

```bash
python -m pytest
python -m ruff check .
python -m pytest tests/e2e
```

## Constraints

- Do not store credentials.
- Do not store Kubernetes tokens.
- Do not store secret sink DSNs or passwords.
