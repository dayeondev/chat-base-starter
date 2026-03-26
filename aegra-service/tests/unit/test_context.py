from react_agent.context import Context


def test_context_reads_environment(monkeypatch):
    monkeypatch.setenv("SYSTEM_PROMPT", "Prompt from env")
    monkeypatch.setenv("MODEL_REF", "openai:gpt-4.1-nano")
    monkeypatch.setenv("PROJECT_NAME", "Demo Project")

    context = Context.from_env()

    assert context.system_prompt == "Prompt from env"
    assert context.model == "openai:gpt-4.1-nano"
    assert context.project_name == "Demo Project"
