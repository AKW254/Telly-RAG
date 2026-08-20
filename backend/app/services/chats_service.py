import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.chats import Chat
from app.models.chatmessages import ChatMessage
from app.schemas.chats_schema import ChatCreate, ChatUpdate,ChatResponse,ChatDetailResponse
from app.schemas.chat_messages_schema import ChatMessageCreate

from app.cache.chat_cache import ChatCache
from app.cache.factory import get_cache


class ChatService:
    TITLE_MAX_LENGTH = 80

    def __init__(self,db: Session, chat_cache: ChatCache| None = None, ):
        self.db = db
        self.chat_cache = (
            chat_cache
            if chat_cache is not None
            else ChatCache(get_cache())
    
            )
        
    # ==========================================================
    # CHAT
    # ==========================================================
     #Create
    def create_chat(self,user_id: int,chat_in: ChatCreate,) -> Chat:

        data = chat_in.model_dump(exclude_unset=True)
        chat = Chat(user_id=user_id, **data)

        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)

        return chat

    @classmethod
    def _title_from_message(cls, content: str) -> str:
        #Create a compact, readable title from the first user message.
        title = re.sub(r"\s+", " ", content).strip()
        if not title:
            return "New chat"

        sentence_end = re.search(r"[.!?](?:\s|$)", title)
        if sentence_end:
            title = title[: sentence_end.end()].rstrip(".!? ")

        if len(title) > cls.TITLE_MAX_LENGTH:
            title = title[: cls.TITLE_MAX_LENGTH - 1].rstrip() + "…"
        return title
    
    #list chat
    def list_chats(self, user_id: int, ) ->ChatResponse:
        chats= self.db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.updated_at).all()
        return chats
    
    # Get Single Chat
    def get_chat(self,chat_id:int ,user_id:int,) -> ChatDetailResponse:
        chat =self.db.query(Chat).options(joinedload(Chat.messages)).filter(Chat.id == chat_id,Chat.user_id == user_id).first()
        return chat
    #Update chat
    def update_chat(self, chat_id: int, user_id: int,chat_in: ChatUpdate,) -> ChatResponse:
        chat = self.get_chat(chat_id=chat_id,user_id=user_id)
        data = chat_in.model_dump(exclude_unset=True)
        
        for field,value in data.items():
            setattr(chat,field,value,)
        self.db.commit()
        self.db.refresh(chat)
        return chat
    #Delete chat
    def delete_chat(self,chat_id:int ,user_id:int,)->bool:
       #Check if exists
       chat =  self.get_chat(chat_id=chat_id, user_id=user_id,)
       if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )
       # Remove cached conversation first.
       self.chat_cache.clear(user_id=user_id,chat_id=chat_id)
       
       #Remove from Database
       self.db.delete(chat)
       self.db.commit()
       return True
    # ==========================================================
    # CHAT MESSAGE
    # ==========================================================
    #User question
    def create_message(self,chat_id: int,user_id: int, message_in: ChatMessageCreate,) -> ChatMessage:
        chat = (self.db.query(Chat).filter(Chat.id == chat_id,Chat.user_id == user_id,).first())

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )
        message = ChatMessage(chat_id=chat_id,role="user",content=message_in.content)

        # Preserve user-supplied titles; otherwise title the chat from its first question.
        if not chat.title or not chat.title.strip():
            chat.title = self._title_from_message(message_in.content)
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message) 
        
        #Add to cache
        self.chat_cache.add_message(user_id=user_id,chat_id=chat_id,role="user",content=message_in.content,) 
        
        return message 
    #AI Response
    def create_assistant_message(self,chat_id: int,user_id: int,content: str,) -> ChatMessage:

        chat = (self.db.query(Chat).filter(Chat.id == chat_id,Chat.user_id == user_id,).first())

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )
            
        # Save assistant response
    
        message = ChatMessage(
            chat_id=chat_id,
            role="assistant",
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # Cache assistant response

        self.chat_cache.add_message(user_id=user_id,chat_id=chat_id,role="assistant",content=content,)

        return message

 
    # LIST MESSAGES
  
    def list_messages(self,chat_id: int, user_id: int,) -> list[ChatMessage]:

        chat = (self.db.query(Chat).filter(Chat.id == chat_id,Chat.user_id == user_id,).first())

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return (self.db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at.asc()).all())

    # ==========================================================
    # GET CONVERSATION HISTORY
    # ==========================================================

    def get_conversation_history(self,chat_id: int,user_id: int,) -> list[dict]:

        chat = (self.db.query(Chat).filter(Chat.id == chat_id,Chat.user_id == user_id,).first())

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        # Try cache first

        cached_messages = self.chat_cache.get_history(user_id=user_id,chat_id=chat_id,)

        if cached_messages:
            return cached_messages

        
        # Cache miss → load from database
       
        messages = (self.db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at.asc()).all())

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]
        
        # Populate cache

        if history:
            self.chat_cache.set_history(user_id=user_id,chat_id=chat_id,messages=history,)
        return history    


        
