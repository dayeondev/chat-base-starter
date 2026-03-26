from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from react_agent.context import Context
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import get_model


async def call_model(state: State, runtime: Runtime[Context]):
    context = runtime.context if runtime.context is not None else Context.from_env()
    model = get_model(context).bind_tools(TOOLS)
    response = await model.ainvoke(
        [SystemMessage(content=context.system_prompt), *state["messages"]]
    )
    return {"messages": [response]}


def route_model_output(state: State) -> str:
    last_message = state["messages"][-1]
    return "tools" if getattr(last_message, "tool_calls", None) else END


builder = StateGraph(State, input_schema=InputState, context_schema=Context)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", route_model_output)
builder.add_edge("tools", "call_model")

graph = builder.compile(name="Aegra React Agent Sample")
