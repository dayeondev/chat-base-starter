from __future__ import annotations

from langchain.chat_models import init_chat_model

from react_agent.context import Context


def split_model_ref(model_ref: str) -> tuple[str, str]:
    if ":" not in model_ref:
        return "openai", model_ref

    provider, model_name = model_ref.split(":", 1)
    return provider, model_name


def get_model(context: Context):
    provider, model_name = split_model_ref(context.model)
    return init_chat_model(model_name, model_provider=provider)
