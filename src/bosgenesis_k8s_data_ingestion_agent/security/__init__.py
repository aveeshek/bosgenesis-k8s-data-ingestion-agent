"""Security policy helpers."""

SENSITIVE_FIELD_NAMES = {
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "client_secret",
}


def redact_sensitive(value):
    """Recursively redact secret-like values from dicts and lists."""

    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_FIELD_NAMES:
                redacted[key] = "***REDACTED***"
            else:
                redacted[key] = redact_sensitive(item)
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def validate_namespace(namespace: str, allowed_namespace: str = "bosgenesis") -> str:
    if namespace != allowed_namespace:
        raise ValueError(f"namespace {namespace!r} is outside allowed scope {allowed_namespace!r}")
    return namespace

