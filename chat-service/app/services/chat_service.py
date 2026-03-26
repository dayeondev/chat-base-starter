from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Conversation
from app.services.aegra_client import AegraClient


class ChatService:
    def __init__(self, aegra_client: AegraClient) -> None:
        self.aegra_client = aegra_client

    async def list_conversations(self, db: Session, user_id: int) -> list[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    async def create_conversation(
        self,
        db: Session,
        user_id: int,
        username: str,
        title: Optional[str],
        request_id: str,
    ) -> Conversation:
        aegra_thread_id = await self.aegra_client.create_thread(request_id)
        conversation = Conversation(
            user_id=user_id,
            username=username,
            title=title or "새 커리어 대화",
            aegra_thread_id=aegra_thread_id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    async def get_conversation(
        self, db: Session, conversation_id: str, user_id: int, request_id: str
    ) -> dict[str, Any]:
        conversation = self._require_conversation(db, conversation_id, user_id)
        state = await self.aegra_client.get_thread_state(
            conversation.aegra_thread_id, request_id
        )
        messages = self._extract_messages(state)
        return {"conversation": conversation, "messages": messages}

    async def send_message(
        self,
        db: Session,
        conversation_id: str,
        user_id: int,
        content: str,
        request_id: str,
    ) -> dict[str, Any]:
        conversation = self._require_conversation(db, conversation_id, user_id)
        result = await self.aegra_client.run_message(
            conversation.aegra_thread_id, content, request_id
        )
        if conversation.title == "새 커리어 대화":
            conversation.title = content[:40]
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return {
            "conversation": conversation,
            "messages": self._normalize_messages(result["messages"]),
        }

    def _require_conversation(
        self, db: Session, conversation_id: str, user_id: int
    ) -> Conversation:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        return conversation

    def _extract_messages(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        values = state.get("values", {})
        return self._normalize_messages(values.get("messages", []))

    def _normalize_messages(
        self, messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return [
            message for message in messages if message.get("type") in {"human", "ai"}
        ]
