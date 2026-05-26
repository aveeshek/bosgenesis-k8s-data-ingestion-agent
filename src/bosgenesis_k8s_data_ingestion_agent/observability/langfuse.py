"""Optional Langfuse tracing integration."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from dataclasses import asdict
import os
from typing import Any

from bosgenesis_k8s_data_ingestion_agent.config import Settings
from bosgenesis_k8s_data_ingestion_agent.models import RunContext, ScanRequest, ScanSummary
from bosgenesis_k8s_data_ingestion_agent.observability.logging import get_logger


class NoopTraceContext:
    trace_id: str | None = None

    def span(
        self,
        name: str,
        *,
        input: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        _ = name, input, metadata
        return nullcontext()

    def update_summary(self, summary: ScanSummary) -> None:
        _ = summary


class NoopLangfuseTracer:
    enabled = False

    def scan(self, request: ScanRequest, run_context: RunContext) -> AbstractContextManager[NoopTraceContext]:
        _ = request, run_context
        return nullcontext(NoopTraceContext())

    def flush(self) -> None:
        return None


class LangfuseTraceContext:
    def __init__(self, client: Any, root_span: Any, trace_id: str | None) -> None:
        self._client = client
        self._root_span = root_span
        self.trace_id = trace_id

    def span(
        self,
        name: str,
        *,
        input: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AbstractContextManager[Any]:
        return self._client.start_as_current_observation(
            as_type="span",
            name=name,
            input=input,
            metadata=metadata,
        )

    def update_summary(self, summary: ScanSummary) -> None:
        self._root_span.update(
            output={
                "status": summary.status.value,
                "resources_seen": summary.resources_seen,
                "resources_changed": summary.resources_changed,
                "helm_releases_seen": summary.helm_releases_seen,
                "helm_releases_changed": summary.helm_releases_changed,
                "sinks_used": list(summary.sinks_used),
                "errors": list(summary.errors),
            },
            metadata={"finished_at": summary.finished_at.isoformat()},
        )


class LangfuseTracer:
    enabled = True

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_settings(cls, settings: Settings) -> "LangfuseTracer | NoopLangfuseTracer":
        logger = get_logger(__name__)
        if not settings.observability.langfuse_enabled:
            return NoopLangfuseTracer()
        if not settings.observability.langfuse_public_key or not settings.observability.langfuse_secret_key:
            logger.warning(
                "langfuse enabled but credentials missing",
                extra={"event": "langfuse_disabled_missing_credentials"},
            )
            return NoopLangfuseTracer()
        try:
            from langfuse import get_client
        except ImportError:
            logger.warning(
                "langfuse package is not installed",
                extra={"event": "langfuse_disabled_missing_package"},
            )
            return NoopLangfuseTracer()

        os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.observability.langfuse_public_key)
        os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.observability.langfuse_secret_key)
        if settings.observability.langfuse_base_url:
            os.environ.setdefault("LANGFUSE_BASE_URL", settings.observability.langfuse_base_url)
        return cls(get_client())

    def scan(self, request: ScanRequest, run_context: RunContext):
        trace_id = self._client.create_trace_id(seed=run_context.correlation_id)
        root_span = self._client.start_as_current_observation(
            as_type="span",
            name="data-ingestion.scan",
            trace_context={"trace_id": trace_id},
            input={
                "request": asdict(request),
                "run_id": str(run_context.run_id),
                "correlation_id": run_context.correlation_id,
            },
            metadata={
                "namespace": run_context.namespace,
                "trigger_type": run_context.trigger_type,
                "service": "bosgenesis-k8s-data-ingestion-agent",
            },
        )
        return _LangfuseScanContext(root_span, self._client, trace_id)

    def flush(self) -> None:
        self._client.flush()


class _LangfuseScanContext:
    def __init__(self, root_span: Any, client: Any, trace_id: str) -> None:
        self._root_span = root_span
        self._client = client
        self._trace_id = trace_id

    def __enter__(self) -> LangfuseTraceContext:
        span = self._root_span.__enter__()
        return LangfuseTraceContext(self._client, span, self._trace_id)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool | None:
        result = self._root_span.__exit__(exc_type, exc, traceback)
        self._client.flush()
        return result
