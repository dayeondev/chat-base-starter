# Aegra Service

This service runs the internal LangGraph agent runtime.

## Role In The Starter

- receives chat execution requests from `chat-service`
- serves the compiled LangGraph graph registered in `aegra.json`
- stores Aegra protocol state in its own Postgres database (`aegradb`)

The browser should not call this service directly in the default starter topology.

## Local Configuration

```bash
cp .env.example .env
```

Required values:

- `OPENAI_API_KEY`

Common values are already documented in `.env.example`.

## Runtime Notes

- Graph entrypoint: `src/react_agent/graph.py`
- Assistant id: `agent`
- Prompt/tool defaults are intentionally starter-oriented and should be replaced when the repo is forked for a real domain
