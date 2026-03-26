from __future__ import annotations

from langchain_core.tools import tool


PROJECT_OVERVIEW = """This starter repository is organized around browser-to-agent chat.

- frontend/: browser UI
- api-gateway/: authentication, routing, and browser entrypoint
- chat-service/: conversation ownership and Aegra relay
- aegra-service/: LangGraph agent runtime served by Aegra

Forking teams are expected to replace the sample domain text and connect their own data sources.
"""


STACK_DETAILS = {
    "frontend": "Frontend uses a browser app that talks only to the API gateway.",
    "gateway": "The gateway validates user JWTs and forwards trusted identity headers downstream.",
    "chat": "The chat service owns conversations and relays browser requests to the Aegra runtime.",
    "aegra": "Aegra exposes the graph as the `agent` assistant and supports streamed runs.",
}


@tool
def get_project_overview() -> str:
    """Return the high-level layout and purpose of this starter."""

    return PROJECT_OVERVIEW.strip()


@tool
def lookup_stack_details(topic: str) -> str:
    """Return a short explanation of the starter for frontend, gateway, chat, or aegra."""

    normalized = topic.strip().lower()
    return STACK_DETAILS.get(normalized, "Available topics: frontend, gateway, chat, aegra.")


TOOLS = [get_project_overview, lookup_stack_details]
