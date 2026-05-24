import pytest

from bosgenesis_k8s_data_ingestion_agent.security import redact_sensitive, validate_namespace


def test_redact_sensitive_nested_values():
    payload = {
        "metadata": {"name": "demo"},
        "password": "secret-value",
        "nested": [{"token": "abc"}],
    }

    redacted = redact_sensitive(payload)

    assert redacted["password"] == "***REDACTED***"
    assert redacted["nested"][0]["token"] == "***REDACTED***"


def test_validate_namespace_rejects_cross_namespace():
    with pytest.raises(ValueError):
        validate_namespace("default", "bosgenesis")

