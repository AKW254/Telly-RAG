from sqlalchemy import Column,DateTime,Integer,String,func
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id =Column(Integer,primary_key=True,index=True,autoincrement=True)
    name = Column(String(255),nullable=False)
    email = Column(String(255),unique=True, index=True, nullable=False)
    password =Column(String(255),nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),onupdate=func.now(),nullable=False)
    
    #Relationship
    chats = relationship("Chat", back_populates="user", cascade="all,delete-orphan")
    documents = relationship("document", back_populates="user", cascade="all,delete-orphan")
    