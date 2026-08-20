from typing import List

from fastapi import (APIRouter, Depends,status,)
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.chats_schema import (
    ChatCreate,
    ChatUpdate,
    ChatDetailResponse,
    ChatResponse,
)

from app.schemas.chat_messages_schema import (
    ChatMessageCreate,
    ChatMessageResponse,
)

from app.models.users import User

from app.api.dependencies import get_current_user

from app.services.chats_service import ChatService
from app.rag.retrieval.RetrieverService import RetrieverService


router = APIRouter()


# ============================================================
# CHAT ROUTES
# ============================================================


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_chat(
    chat_in: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):


    service = ChatService(db)

    return service.create_chat(
        user_id=current_user.id,
        chat_in=chat_in,
    )


# ============================================================
# LIST CHATS
# ============================================================


@router.get(
    "/",
    response_model=List[ChatResponse],
)
def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all chats belonging to the authenticated user.
    """

    service = ChatService(db)

    return service.list_chats(
        user_id=current_user.id,
    )


# ============================================================
# GET CHAT
# ============================================================


@router.get(
    "/{chat_id}",
    response_model=ChatDetailResponse,
)
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return a chat together with its messages.
    """

    service = ChatService(db)

    return service.get_chat(
        chat_id=chat_id,
        user_id=current_user.id,
    )


# ============================================================
# UPDATE CHAT
# ============================================================


@router.put(
    "/{chat_id}",
    response_model=ChatResponse,
)
def update_chat(
    chat_id: int,
    chat_in: ChatUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a chat belonging to the authenticated user.
    """

    service = ChatService(db)

    return service.update_chat(
        chat_id=chat_id,
        user_id=current_user.id,
        chat_in=chat_in,
    )


# ============================================================
# DELETE CHAT
# ============================================================


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a chat and its messages.
    """

    service = ChatService(db)

    service.delete_chat(
        chat_id=chat_id,
        user_id=current_user.id,
    )

    return None


# ============================================================
# CHAT MESSAGE ROUTES
# ============================================================


@router.post(
    "/{chat_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    chat_id: int,
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
   

    service = ChatService(db)

    return service.process_message(
        chat_id=chat_id,
        user_id=current_user.id,
        message_in=message_in,
    )


# ============================================================
# LIST CHAT MESSAGES
# ============================================================


@router.get(
    "/{chat_id}/messages",
    response_model=List[ChatMessageResponse],
)
def list_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all messages belonging to a chat.
    """

    service = ChatService(db)

    return service.list_messages(
        chat_id=chat_id,
        user_id=current_user.id,
    )