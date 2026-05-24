"""Normalization pipeline."""

from __future__ import annotations

from bosgenesis_k8s_data_ingestion_agent.models import Observation, RawBundle, RunContext
from bosgenesis_k8s_data_ingestion_agent.normalizers.helm import normalize_helm_bundle
from bosgenesis_k8s_data_ingestion_agent.normalizers.k8s import normalize_k8s_bundle


def normalize_all(bundles: list[RawBundle], run_context: RunContext) -> list[Observation]:
    observations: list[Observation] = []
    for bundle in bundles:
        if bundle.source == "k8s_mcp":
            observations.extend(normalize_k8s_bundle(bundle, run_context))
        elif bundle.source == "helm_mcp":
            observations.extend(normalize_helm_bundle(bundle, run_context))
    return observations

