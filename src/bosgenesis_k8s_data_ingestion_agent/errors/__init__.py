"""Domain errors for the ingestion agent."""


class IngestionAgentError(Exception):
    """Base class for domain-specific ingestion agent errors."""


class ConfigurationError(IngestionAgentError):
    """Raised when runtime configuration is invalid."""


class ToolDeniedError(IngestionAgentError):
    """Raised when a requested MCP tool is not allowed."""


class McpClientError(IngestionAgentError):
    """Raised when an MCP call fails."""


class NormalizationError(IngestionAgentError):
    """Raised when raw payloads cannot be normalized."""


class SinkWriteError(IngestionAgentError):
    """Raised when a sink write fails and strict mode is enabled."""

