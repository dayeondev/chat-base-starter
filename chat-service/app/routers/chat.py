from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth import AuthenticatedUser, require_gateway_user
from app.database import get_db
from app.schemas import (
    ConversationCreate,
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary,
    MessageCreate,
    MessageResponse,
)
from app.services.aegra_client import AegraClient, AegraClientError
from app.services.chat_service import ChatService

router = APIRouter()


def get_chat_service() -> ChatService:
    return ChatService(AegraClient())


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user: AuthenticatedUser = Depends(require_gateway_user),
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    conversations = await chat_service.list_conversations(db, user.user_id)
    return {"conversations": conversations}


@router.post("/conversations", response_model=ConversationSummary)
async def create_conversation(
    payload: ConversationCreate,
    request: Request,
    user: AuthenticatedUser = Depends(require_gateway_user),
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.create_conversation(
        db,
        user.user_id,
        user.username,
        payload.title,
        request.state.request_id,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(require_gateway_user),
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        result = await chat_service.get_conversation(
            db, conversation_id, user.user_id, request.state.request_id
        )
    except AegraClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        **ConversationSummary.model_validate(result["conversation"]).model_dump(),
        "messages": result["messages"],
    }


@router.post(
    "/conversations/{conversation_id}/messages", response_model=MessageResponse
)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    request: Request,
    user: AuthenticatedUser = Depends(require_gateway_user),
    db: Session = Depends(get_db),
    chat_service: ChatService = Depends(get_chat_service),
):
    try:
        result = await chat_service.send_message(
            db,
            conversation_id,
            user.user_id,
            payload.content,
            request.state.request_id,
        )
    except AegraClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "conversation": ConversationSummary.model_validate(result["conversation"]),
        "messages": result["messages"],
    }
