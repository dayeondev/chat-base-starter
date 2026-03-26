from __future__ import annotations

import os
from dataclasses import dataclass

from react_agent.prompts import DEFAULT_SYSTEM_PROMPT


@dataclass
class Context:
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    model: str = "openai:gpt-4.1-mini"
    project_name: str = "Forkable Aegra Starter"

    @classmethod
    def from_env(cls) -> "Context":
        return cls(
            system_prompt=os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
            model=os.getenv("MODEL_REF", "openai:gpt-4.1-mini"),
            project_name=os.getenv("PROJECT_NAME", "Forkable Aegra Starter"),
        )
