from bosgenesis_k8s_data_ingestion_agent.config import Settings


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("AGENT_NAMESPACE", "bosgenesis")
    monkeypatch.setenv("AGENT_RUN_ON_STARTUP", "true")
    monkeypatch.setenv("AGENT_SCAN_INTERVAL_SECONDS", "60")
    monkeypatch.setenv("REDIS_ENABLED", "true")

    settings = Settings.from_env()

    assert settings.agent.namespace == "bosgenesis"
    assert settings.agent.run_on_startup is True
    assert settings.agent.scan_interval_seconds == 60
    assert settings.sinks.redis_enabled is True
    assert settings.observability.langfuse_enabled is True


def test_langfuse_can_be_disabled(monkeypatch):
    monkeypatch.setenv("LANGFUSE_ENABLED", "false")

    settings = Settings.from_env()

    assert settings.observability.langfuse_enabled is False


def test_effective_safe_dict_redacts_langfuse_secret(monkeypatch):
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "secret-value")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "public-value")

    effective = Settings.from_env().effective_safe_dict()

    assert effective["observability"]["langfuse_public_key"] == "public-value"
    assert effective["observability"]["langfuse_secret_key"] == "***REDACTED***"


def test_mcp_allowed_hosts_from_env(monkeypatch):
    monkeypatch.setenv("MCP_ALLOWED_HOSTS", "data-ingestion-agent.bosgenesis.local,localhost")

    settings = Settings.from_env()

    assert settings.api.mcp_allowed_hosts == (
        "data-ingestion-agent.bosgenesis.local",
        "localhost",
    )


def test_mcp_host_headers_from_env(monkeypatch):
    monkeypatch.setenv("K8S_MCP_HOST_HEADER", "k8s-inspector.bosgenesis.local")
    monkeypatch.setenv("HELM_MCP_HOST_HEADER", "helm-manager.bosgenesis.local")

    settings = Settings.from_env()

    assert settings.k8s_mcp.host_header == "k8s-inspector.bosgenesis.local"
    assert settings.helm_mcp.host_header == "helm-manager.bosgenesis.local"


def test_effective_safe_dict_contains_no_secret_keys():
    settings = Settings.from_env()

    effective = settings.effective_safe_dict()

    assert "agent" in effective
    assert "secret-value" not in str(effective)


def test_effective_safe_dict_redacts_sink_secrets(monkeypatch):
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "secret-value")
    monkeypatch.setenv("REDIS_PASSWORD", "secret-value")

    effective = Settings.from_env().effective_safe_dict()

    assert effective["sinks"]["clickhouse_password"] == "***REDACTED***"
    assert effective["sinks"]["redis_password"] == "***REDACTED***"
