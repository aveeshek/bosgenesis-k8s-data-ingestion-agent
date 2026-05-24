# Runtime Config Module Specification

## Role

This module will load, validate, and expose typed runtime settings.

## Responsibilities

- Model all settings with typed validation.
- Merge defaults, config file values, and environment variables.
- Mask secrets in effective config responses.
- Validate compatible sink and memory settings.

## Required settings classes

- Agent settings.
- API settings.
- Scheduler settings.
- MCP settings.
- Sink settings.
- Memory settings.
- Observability settings.
- Security settings.

