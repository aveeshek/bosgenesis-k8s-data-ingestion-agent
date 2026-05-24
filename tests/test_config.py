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
