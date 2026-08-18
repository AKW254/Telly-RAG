from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column( Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False,index=True,)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(100), nullable=True)
    mime_type = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String(50),nullable=False,default="pending",)
    # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False,)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False,)

    # Relationships
    user = relationship("User", back_populates="documents")
    