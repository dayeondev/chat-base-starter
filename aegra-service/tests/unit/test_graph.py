from langchain_core.messages import AIMessage
from langgraph.graph import END

from react_agent.graph import graph, route_model_output
from react_agent.state import State


def test_graph_compiles():
    assert graph is not None


def test_route_model_output_ends_without_tool_calls():
    state: State = {"messages": [AIMessage(content="done")]}

    assert route_model_output(state) == END


def test_route_model_output_routes_to_tools_with_tool_calls():
    state: State = {
        "messages": [
            AIMessage(
                content="calling tool",
                tool_calls=[{"name": "get_project_overview", "args": {}, "id": "call_1"}],
            )
        ]
    }

    assert route_model_output(state) == "tools"
