from datetime import datetime
from typing import List, Optional
from app.schemas.chat_messages_schema import ChatMessageResponse
from pydantic import BaseModel, ConfigDict, Field

# ==========================================
# Chat Schemas
# ==========================================

class ChatBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)


class ChatCreate(ChatBase):
    pass


class ChatUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)


class ChatResponse(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetailResponse(ChatResponse):
    messages: List[ChatMessageResponse] = []




