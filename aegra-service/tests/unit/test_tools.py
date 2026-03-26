from react_agent.tools import get_project_overview, lookup_stack_details


def test_get_project_overview_returns_backend_and_web():
    result = get_project_overview.invoke({})

    assert "backend/" in result
    assert "web/" in result


def test_lookup_stack_details_handles_known_and_unknown_topics():
    assert "Aegra" in lookup_stack_details.invoke({"topic": "backend"})
    assert "Available topics" in lookup_stack_details.invoke({"topic": "unknown"})
