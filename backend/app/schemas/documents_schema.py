from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from .users_schema import UserResponse

# ==========================================
# Document Schemas
# ==========================================

class DocumentBase(BaseModel):
    filename: str = Field(..., max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=100)
    mime_type: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None


class DocumentCreate(DocumentBase):
    status: Optional[str] = Field(
        "pending", 
        max_length=50, 
        description="pending, processing, completed, failed"
    )


class DocumentUpdate(BaseModel):
    filename: Optional[str] = Field(None, max_length=255)
    file_path: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=100)
    mime_type: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserResponse] = None
    model_config = ConfigDict(from_attributes=True)