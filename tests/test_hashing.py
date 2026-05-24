from bosgenesis_k8s_data_ingestion_agent.hashing import compute_content_hash, remove_volatile_fields


def test_hash_ignores_volatile_fields():
    first = {"metadata": {"name": "pod", "resourceVersion": "1"}, "status": {"phase": "Running"}}
    second = {"metadata": {"name": "pod", "resourceVersion": "2"}, "status": {"phase": "Running"}}

    assert compute_content_hash(first) == compute_content_hash(second)


def test_remove_volatile_fields_nested():
    payload = {"managedFields": [], "nested": {"lastTransitionTime": "now", "stable": "yes"}}

    cleaned = remove_volatile_fields(payload)

    assert "managedFields" not in cleaned
    assert "lastTransitionTime" not in cleaned["nested"]
    assert cleaned["nested"]["stable"] == "yes"

