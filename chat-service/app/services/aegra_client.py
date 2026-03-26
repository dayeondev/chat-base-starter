import json
import os
from typing import Any, Optional

import httpx


class AegraClientError(Exception):
    pass


class AegraClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("AEGRA_API_URL", "http://aegra-service:2026")
        self.assistant_id = os.getenv("AEGRA_ASSISTANT_ID", "agent")
        self.timeout = httpx.Timeout(60.0, connect=5.0)

    async def create_thread(self, request_id: str) -> str:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout
        ) as client:
            response = await client.post(
                "/threads",
                json={"metadata": {"graph_id": self.assistant_id}},
                headers=self._headers(request_id),
            )
            response.raise_for_status()
            return response.json()["thread_id"]

    async def get_thread_state(self, thread_id: str, request_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout
        ) as client:
            response = await client.get(
                f"/threads/{thread_id}/state",
                headers=self._headers(request_id),
            )
            response.raise_for_status()
            return response.json()

    async def run_message(
        self, thread_id: str, content: str, request_id: str
    ) -> dict[str, Any]:
        latest_messages: Optional[list[dict[str, Any]]] = None
        current_event = "message"
        payload = {
            "assistant_id": self.assistant_id,
            "input": {
                "messages": [
                    {
                        "type": "human",
                        "content": content,
                    }
                ]
            },
            "stream_mode": "values",
        }

        async with httpx.AsyncClient(base_url=self.base_url, timeout=None) as client:
            async with client.stream(
                "POST",
                f"/threads/{thread_id}/runs/stream",
                json=payload,
                headers={**self._headers(request_id), "Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        current_event = "message"
                        continue
                    if line.startswith("event:"):
                        current_event = line.split(":", 1)[1].strip()
                        continue
                    if not line.startswith("data:"):
                        continue

                    raw = line.split(":", 1)[1].strip()
                    if not raw:
                        continue

                    data = json.loads(raw)
                    if current_event == "error":
                        message = data.get("message", "Aegra stream failed")
                        raise AegraClientError(message)

                    if current_event == "values" and isinstance(data, dict):
                        candidate = data.get("messages")
                        if isinstance(candidate, list):
                            latest_messages = candidate

        if latest_messages is None:
            state = await self.get_thread_state(thread_id, request_id)
            latest_messages = state.get("values", {}).get("messages", [])

        return {"messages": latest_messages}

    def _headers(self, request_id: str) -> dict[str, str]:
        return {"X-Request-ID": request_id}
