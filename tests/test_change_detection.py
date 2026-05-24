from uuid import uuid4

from bosgenesis_k8s_data_ingestion_agent.change_detection import ChangeDetector, InMemoryHashStateStore
from bosgenesis_k8s_data_ingestion_agent.models import ChangeType, Observation, RunContext


def observation(content_hash: str) -> Observation:
    context = RunContext()
    return Observation(
        observation_id=uuid4(),
        run_id=context.run_id,
        source="k8s_mcp",
        namespace="bosgenesis",
        entity_type="Pod",
        entity_name="pod-a",
        entity_uid="uid-a",
        observed_at=context.started_at,
        status_summary="Running",
        raw_payload={},
        normalized_payload={"name": "pod-a"},
        hash_input={"name": "pod-a"},
        content_hash=content_hash,
    )


def test_detect_new_then_unchanged():
    detector = ChangeDetector(store=InMemoryHashStateStore())

    first = detector.detect([observation("hash-1")])
    second = detector.detect([observation("hash-1")])

    assert first[0].change_type == ChangeType.NEW
    assert second[0].change_type == ChangeType.UNCHANGED


def test_detect_changed():
    detector = ChangeDetector(store=InMemoryHashStateStore())

    detector.detect([observation("hash-1")])
    changed = detector.detect([observation("hash-2")])

    assert changed[0].change_type == ChangeType.CHANGED
    assert changed[0].previous_hash == "hash-1"

