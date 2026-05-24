from bosgenesis_k8s_data_ingestion_agent.models import RawBundle, RunContext
from bosgenesis_k8s_data_ingestion_agent.normalizers import normalize_all, normalize_helm_bundle, normalize_k8s_bundle


def test_k8s_normalizer_creates_observation_and_redacts_secrets():
    bundle = RawBundle(
        source="k8s_mcp",
        namespace="bosgenesis",
        payload={
            "pods": {
                "items": [
                    {
                        "kind": "Pod",
                        "metadata": {"name": "pod-a", "uid": "uid-a"},
                        "status": {"phase": "Running"},
                        "spec": {"password": "nope"},
                    }
                ]
            }
        },
    )

    observations = normalize_k8s_bundle(bundle, RunContext())

    assert observations[0].entity_type == "Pod"
    assert observations[0].entity_name == "pod-a"
    assert observations[0].status_summary == "Running"
    assert observations[0].normalized_payload["spec"]["password"] == "***REDACTED***"


def test_helm_normalizer_creates_release_observation():
    bundle = RawBundle(
        source="helm_mcp",
        namespace="bosgenesis",
        payload={"releases": [{"release": {"name": "demo"}, "status": {"status": "deployed"}}]},
    )

    observations = normalize_helm_bundle(bundle, RunContext())

    assert observations[0].entity_type == "HelmRelease"
    assert observations[0].entity_name == "demo"


def test_normalize_all_routes_by_source():
    context = RunContext()
    observations = normalize_all(
        [
            RawBundle(
                source="k8s_mcp",
                namespace="bosgenesis",
                payload={"services": {"items": [{"metadata": {"name": "svc"}}]}},
            )
        ],
        context,
    )

    assert len(observations) == 1

