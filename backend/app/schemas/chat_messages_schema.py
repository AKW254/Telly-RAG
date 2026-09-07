from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

# ==========================================
# ChatMessage Schemas
# ==========================================

class ChatMessageBase(BaseModel):
    role: str = Field(..., max_length=20, description="e.g., user, assistant, system")
    content: str


class ChatMessageCreate(ChatMessageBase):
    role: Optional[str] = None


class ChatMessageResponse(ChatMessageBase):
    id: int
    chat_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)