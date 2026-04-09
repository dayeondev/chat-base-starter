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
        self.connect_timeout_seconds = self._get_positive_float_env(
            "AEGRA_CONNECT_TIMEOUT_SECONDS", 5.0
        )
        self.state_timeout_seconds = self._get_positive_float_env(
            "AEGRA_STATE_TIMEOUT_SECONDS", 60.0
        )
        self.request_timeout = httpx.Timeout(
            self.state_timeout_seconds, connect=self.connect_timeout_seconds
        )

    @staticmethod
    def _get_positive_float_env(name: str, default: float) -> float:
        raw = os.getenv(name, str(default))
        try:
            value = float(raw)
        except ValueError as exc:
            raise ValueError(f"{name} must be a positive number, got: {raw!r}") from exc
        if value <= 0:
            raise ValueError(f"{name} must be > 0, got: {value}")
        return value

    async def create_thread(self, request_id: str) -> str:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.request_timeout
        ) as client:
            try:
                response = await client.post(
                    "/threads",
                    json={"metadata": {"graph_id": self.assistant_id}},
                    headers=self._headers(request_id),
                )
            except httpx.TimeoutException as exc:
                raise AegraClientError(
                    "Timed out while creating a thread in aegra-service. "
                    f"Increase AEGRA_STATE_TIMEOUT_SECONDS if your agent setup is slow. "
                    f"assistant_id={self.assistant_id}"
                ) from exc
            response.raise_for_status()
            return response.json()["thread_id"]

    async def get_thread_state(self, thread_id: str, request_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.request_timeout
        ) as client:
            try:
                response = await client.get(
                    f"/threads/{thread_id}/state",
                    headers=self._headers(request_id),
                )
            except httpx.TimeoutException as exc:
                raise AegraClientError(
                    "Timed out while fetching thread state from aegra-service. "
                    f"Increase AEGRA_STATE_TIMEOUT_SECONDS if your agent runs are slow. "
                    f"thread_id={thread_id}"
                ) from exc
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
