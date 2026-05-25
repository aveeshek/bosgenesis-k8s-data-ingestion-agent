"""Runtime configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _env_csv(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


@dataclass(frozen=True)
class AgentSettings:
    namespace: str = "bosgenesis"
    run_on_startup: bool = False
    scan_interval_seconds: int = 300
    strict_sinks: bool = False


@dataclass(frozen=True)
class ApiSettings:
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080
    mcp_allowed_hosts: tuple[str, ...] = (
        "data-ingestion-agent.bosgenesis.local",
        "bosgenesis-k8s-data-ingestion-agent",
        "bosgenesis-k8s-data-ingestion-agent.bosgenesis",
        "bosgenesis-k8s-data-ingestion-agent.bosgenesis.svc",
        "bosgenesis-k8s-data-ingestion-agent.bosgenesis.svc.cluster.local",
        "localhost",
        "127.0.0.1",
    )


@dataclass(frozen=True)
class McpEndpointSettings:
    enabled: bool = True
    url: str = ""
    host_header: str | None = None
    timeout_seconds: int = 30
    retries: int = 2


@dataclass(frozen=True)
class SinkSettings:
    postgres_enabled: bool = False
    postgres_dsn: str | None = None
    clickhouse_enabled: bool = False
    clickhouse_host: str = "clickhouse.bosgenesis.svc.cluster.local"
    clickhouse_port: int = 8123
    clickhouse_user: str = "bosgenesis"
    clickhouse_password: str | None = None
    clickhouse_database: str = "bosgenesis_k8s_ingestion"
    qdrant_enabled: bool = False
    qdrant_url: str = "http://qdrant.bosgenesis.svc.cluster.local:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "bosgenesis_k8s_observations"
    qdrant_vector_size: int = 1536
    pgvector_enabled: bool = False
    redis_enabled: bool = False
    redis_host: str = "redis-master.bosgenesis.svc.cluster.local"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None
    redis_key_prefix: str = "bg:k8s-ingestion"
    stdout_enabled: bool = True


@dataclass(frozen=True)
class ObservabilitySettings:
    log_level: str = "INFO"
    service_name: str = "bosgenesis-k8s-data-ingestion-agent"
    langfuse_enabled: bool = False
    signoz_enabled: bool = False


@dataclass(frozen=True)
class Settings:
    agent: AgentSettings = field(default_factory=AgentSettings)
    api: ApiSettings = field(default_factory=ApiSettings)
    k8s_mcp: McpEndpointSettings = field(
        default_factory=lambda: McpEndpointSettings(
            url="http://k8s-inspector.bosgenesis.local/mcp"
        )
    )
    helm_mcp: McpEndpointSettings = field(
        default_factory=lambda: McpEndpointSettings(url="http://helm-manager.bosgenesis.local/mcp")
    )
    sinks: SinkSettings = field(default_factory=SinkSettings)
    observability: ObservabilitySettings = field(default_factory=ObservabilitySettings)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            agent=AgentSettings(
                namespace=os.getenv("AGENT_NAMESPACE", "bosgenesis"),
                run_on_startup=_env_bool("AGENT_RUN_ON_STARTUP", False),
                scan_interval_seconds=_env_int("AGENT_SCAN_INTERVAL_SECONDS", 300),
                strict_sinks=_env_bool("AGENT_STRICT_SINKS", False),
            ),
            api=ApiSettings(
                enabled=_env_bool("API_ENABLED", True),
                host=os.getenv("API_HOST", "0.0.0.0"),
                port=_env_int("API_PORT", 8080),
                mcp_allowed_hosts=_env_csv(
                    "MCP_ALLOWED_HOSTS",
                    ApiSettings().mcp_allowed_hosts,
                ),
            ),
            k8s_mcp=McpEndpointSettings(
                enabled=_env_bool("K8S_MCP_ENABLED", True),
                url=os.getenv("K8S_MCP_URL", "http://k8s-inspector.bosgenesis.local/mcp"),
                host_header=os.getenv("K8S_MCP_HOST_HEADER"),
                timeout_seconds=_env_int("K8S_MCP_TIMEOUT_SECONDS", 30),
                retries=_env_int("K8S_MCP_RETRIES", 2),
            ),
            helm_mcp=McpEndpointSettings(
                enabled=_env_bool("HELM_MCP_ENABLED", True),
                url=os.getenv("HELM_MCP_URL", "http://helm-manager.bosgenesis.local/mcp"),
                host_header=os.getenv("HELM_MCP_HOST_HEADER"),
                timeout_seconds=_env_int("HELM_MCP_TIMEOUT_SECONDS", 30),
                retries=_env_int("HELM_MCP_RETRIES", 2),
            ),
            sinks=SinkSettings(
                postgres_enabled=_env_bool("POSTGRES_ENABLED", False),
                postgres_dsn=os.getenv("POSTGRES_DSN"),
                clickhouse_enabled=_env_bool("CLICKHOUSE_ENABLED", False),
                clickhouse_host=os.getenv(
                    "CLICKHOUSE_HOST", "clickhouse.bosgenesis.svc.cluster.local"
                ),
                clickhouse_port=_env_int("CLICKHOUSE_PORT", 8123),
                clickhouse_user=os.getenv("CLICKHOUSE_USER", "bosgenesis"),
                clickhouse_password=os.getenv("CLICKHOUSE_PASSWORD"),
                clickhouse_database=os.getenv(
                    "CLICKHOUSE_DATABASE", "bosgenesis_k8s_ingestion"
                ),
                qdrant_enabled=_env_bool("QDRANT_ENABLED", False),
                qdrant_url=os.getenv(
                    "QDRANT_URL", "http://qdrant.bosgenesis.svc.cluster.local:6333"
                ),
                qdrant_api_key=os.getenv("QDRANT_API_KEY"),
                qdrant_collection=os.getenv("QDRANT_COLLECTION", "bosgenesis_k8s_observations"),
                qdrant_vector_size=_env_int("QDRANT_VECTOR_SIZE", 1536),
                pgvector_enabled=_env_bool("PGVECTOR_ENABLED", False),
                redis_enabled=_env_bool("REDIS_ENABLED", False),
                redis_host=os.getenv("REDIS_HOST", "redis-master.bosgenesis.svc.cluster.local"),
                redis_port=_env_int("REDIS_PORT", 6379),
                redis_db=_env_int("REDIS_DB", 0),
                redis_password=os.getenv("REDIS_PASSWORD"),
                redis_key_prefix=os.getenv("REDIS_KEY_PREFIX", "bg:k8s-ingestion"),
                stdout_enabled=_env_bool("STDOUT_ENABLED", True),
            ),
            observability=ObservabilitySettings(
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                service_name=os.getenv(
                    "OTEL_SERVICE_NAME", "bosgenesis-k8s-data-ingestion-agent"
                ),
                langfuse_enabled=_env_bool("LANGFUSE_ENABLED", False),
                signoz_enabled=_env_bool("SIGNOZ_ENABLED", False),
            ),
        )

    def effective_safe_dict(self) -> dict[str, object]:
        sink_values = dict(self.sinks.__dict__)
        for secret_key in ("postgres_dsn", "clickhouse_password", "qdrant_api_key", "redis_password"):
            if sink_values.get(secret_key):
                sink_values[secret_key] = "***REDACTED***"
        return {
            "agent": self.agent.__dict__,
            "api": self.api.__dict__,
            "k8s_mcp": self.k8s_mcp.__dict__,
            "helm_mcp": self.helm_mcp.__dict__,
            "sinks": sink_values,
            "observability": self.observability.__dict__,
        }
