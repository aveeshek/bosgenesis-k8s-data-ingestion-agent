import json
import logging

from bosgenesis_k8s_data_ingestion_agent.observability import JsonFormatter


def test_json_formatter_includes_extra_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.run_id = "run-1"
    record.event = "unit_test"

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "hello"
    assert payload["run_id"] == "run-1"
    assert payload["event"] == "unit_test"

