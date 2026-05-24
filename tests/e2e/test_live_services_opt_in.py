import os

import pytest


pytestmark = pytest.mark.live_e2e


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_E2E") != "true",
    reason="set RUN_LIVE_E2E=true to run live BOS Genesis service checks",
)
def test_live_e2e_placeholder_documents_required_env():
    """Placeholder guard for future live cluster checks.

    Live e2e should verify the deployed service endpoints, not unit-level fakes.
    Required values:
    - AGENT_BASE_URL, for example http://data-ingestion-agent.bosgenesis.local
    - RUN_LIVE_E2E=true
    """

    assert os.getenv("AGENT_BASE_URL"), "AGENT_BASE_URL is required for live e2e"

