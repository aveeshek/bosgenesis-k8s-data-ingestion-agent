# Errors Module Specification

## Implemented status

The errors module defines domain-specific exception classes.

## Implemented errors

- `IngestionAgentError`
- `ConfigurationError`
- `ToolDeniedError`
- `McpClientError`
- `NormalizationError`
- `SinkWriteError`

## Usage

- MCP policy raises `ToolDeniedError`.
- MCP transport wrapper raises `McpClientError`.
- Sink router raises `SinkWriteError` in strict mode.
