from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    id: Optional[str] = None
    type: str
    content: Any
    tool_calls: Optional[list[dict[str, Any]]] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationSummary):
    messages: list[ChatMessage]


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    conversation: ConversationSummary
    messages: list[ChatMessage]


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
