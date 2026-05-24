"""Helm payload normalization."""

from __future__ import annotations

from typing import Any

from bosgenesis_k8s_data_ingestion_agent.models import Observation, RawBundle, RunContext
from bosgenesis_k8s_data_ingestion_agent.normalizers.common import make_observation


def _release_name(bundle: dict[str, Any]) -> str:
    release = bundle.get("release")
    status = bundle.get("status")
    if isinstance(release, dict):
        value = release.get("name") or release.get("release_name")
        if value:
            return str(value)
    if isinstance(status, dict):
        value = status.get("name") or status.get("release_name")
        if value:
            return str(value)
    return "unknown"


def normalize_helm_bundle(bundle: RawBundle, run_context: RunContext) -> list[Observation]:
    observations: list[Observation] = []
    releases = bundle.payload.get("releases", [])
    if not isinstance(releases, list):
        return observations
    for release_bundle in releases:
        if not isinstance(release_bundle, dict):
            continue
        release = release_bundle.get("release") if isinstance(release_bundle.get("release"), dict) else {}
        status = release_bundle.get("status") if isinstance(release_bundle.get("status"), dict) else {}
        name = _release_name(release_bundle)
        normalized = {
            "release": release,
            "status": status,
            "history": release_bundle.get("history", []),
            "values": release_bundle.get("values", {}),
            "manifest": release_bundle.get("manifest"),
        }
        observations.append(
            make_observation(
                run_context=run_context,
                source=bundle.source,
                namespace=bundle.namespace,
                entity_type="HelmRelease",
                entity_name=name,
                entity_uid=None,
                raw_payload=release_bundle,
                normalized_payload=normalized,
                status_summary=status.get("status") or release.get("status"),
            )
        )
    return observations

