from sqlalchemy import Column, DateTime, ForeignKey, Integer, String,func
from sqlalchemy.orm import relationship

from app.database import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False, index=True,)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False,)
    updated_at = Column( DateTime(timezone=True),server_default=func.now(), onupdate=func.now(),nullable=False,)

    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="chat",cascade="all, delete-orphan",order_by="ChatMessage.created_at",)


