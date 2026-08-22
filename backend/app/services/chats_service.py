import re

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.chats import Chat
from app.models.chatmessages import ChatMessage
from app.schemas.chats_schema import ChatCreate, ChatUpdate
from app.schemas.chat_messages_schema import ChatMessageCreate

from app.cache.chat_cache import ChatCache
from app.cache.factory import get_cache

from app.rag.retrieval.RetrieverService import RetrieverService
from app.llm.agent import build_agent

from app.rag.generation.tools.document_email_tool import create_document_email_tool
from app.rag.generation.tools.find_document_tool import create_find_document_tool


class ChatService:

    TITLE_MAX_LENGTH = 80

    def __init__(
        self,
        db: Session,
        chat_cache: ChatCache | None = None,
        retriever: RetrieverService | None = None,
    ):
        self.db = db

        self.chat_cache = (
            chat_cache
            if chat_cache is not None
            else ChatCache(get_cache())
        )

        self.retriever = (
            retriever
            if retriever is not None
            else RetrieverService()
        )

    # ==========================================================
    # CHAT
    # ==========================================================

    def create_chat(
        self,
        user_id: int,
        chat_in: ChatCreate,
    ) -> Chat:

        data = chat_in.model_dump(
            exclude_unset=True
        )

        chat = Chat(
            user_id=user_id,
            **data,
        )

        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)

        return chat

    @classmethod
    def _title_from_message(
        cls,
        content: str,
    ) -> str:

        title = re.sub(
            r"\s+",
            " ",
            content,
        ).strip()

        if not title:
            return "New chat"

        sentence_end = re.search(
            r"[.!?](?:\s|$)",
            title,
        )

        if sentence_end:
            title = title[
                :sentence_end.end()
            ].rstrip(".!? ")

        if len(title) > cls.TITLE_MAX_LENGTH:
            title = (
                title[
                    : cls.TITLE_MAX_LENGTH - 1
                ].rstrip()
                + "…"
            )

        return title

    def list_chats(
        self,
        user_id: int,
    ) -> list[Chat]:

        return (
            self.db.query(Chat)
            .filter(
                Chat.user_id == user_id
            )
            .order_by(
                Chat.updated_at.desc()
            )
            .all()
        )

    def get_chat(
        self,
        chat_id: int,
        user_id: int,
    ) -> Chat:

        chat = (
            self.db.query(Chat)
            .options(
                joinedload(Chat.messages)
            )
            .filter(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return chat

    def update_chat(
        self,
        chat_id: int,
        user_id: int,
        chat_in: ChatUpdate,
    ) -> Chat:

        chat = self.get_chat(
            chat_id=chat_id,
            user_id=user_id,
        )

        data = chat_in.model_dump(
            exclude_unset=True
        )

        for field, value in data.items():
            setattr(
                chat,
                field,
                value,
            )

        self.db.commit()
        self.db.refresh(chat)

        return chat

    def delete_chat(
        self,
        chat_id: int,
        user_id: int,
    ) -> bool:

        chat = self.get_chat(
            chat_id=chat_id,
            user_id=user_id,
        )

        self.chat_cache.clear(
            user_id=user_id,
            chat_id=chat_id,
        )

        self.db.delete(chat)
        self.db.commit()

        return True

    # ==========================================================
    # ASSISTANT MESSAGE
    # ==========================================================

    def create_assistant_message(
        self,
        chat_id: int,
        user_id: int,
        content: str,
    ) -> ChatMessage:

        chat = (
            self.db.query(Chat)
            .filter(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        message = ChatMessage(
            chat_id=chat_id,
            role="assistant",
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        self.chat_cache.add_message(
            user_id=user_id,
            chat_id=chat_id,
            role="assistant",
            content=content,
        )

        return message

    # ==========================================================
    # CHAT HISTORY
    # ==========================================================

    def get_conversation_history(
        self,
        chat_id: int,
        user_id: int,
    ) -> list[dict]:

        chat = (
            self.db.query(Chat)
            .filter(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        cached_messages = (
            self.chat_cache.get_history(
                user_id=user_id,
                chat_id=chat_id,
            )
        )

        if cached_messages:
            return cached_messages

        messages = (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.chat_id == chat_id
            )
            .order_by(
                ChatMessage.created_at.asc()
            )
            .all()
        )

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        if history:
            self.chat_cache.set_history(
                user_id=user_id,
                chat_id=chat_id,
                messages=history,
            )

        return history

    # ==========================================================
    # RAG + AGENT PIPELINE
    # ==========================================================

    async def process_message(
        self,
        chat_id: int,
        user_id: int,
        user_name: str,
        user_email: str,
        message_in: ChatMessageCreate,
    ) -> ChatMessage:

        # ------------------------------------------------------
        # 1. Verify chat ownership
        # ------------------------------------------------------

        chat = (
            self.db.query(Chat)
            .filter(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        # ------------------------------------------------------
        # 2. Get PREVIOUS conversation history
        # ------------------------------------------------------

        history = self.get_conversation_history(
            chat_id=chat_id,
            user_id=user_id,
        )

        # ------------------------------------------------------
        # 3. Save user message
        # ------------------------------------------------------

        user_message = ChatMessage(
            chat_id=chat_id,
            role="user",
            content=message_in.content,
        )

        if not chat.title or not chat.title.strip():
            chat.title = self._title_from_message(
                message_in.content
            )

        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)

        # ------------------------------------------------------
        # 4. Cache user message
        # ------------------------------------------------------

        self.chat_cache.add_message(
            user_id=user_id,
            chat_id=chat_id,
            role="user",
            content=message_in.content,
        )

        # ------------------------------------------------------
        # 5. RETRIEVAL
        # ------------------------------------------------------

        documents = self.retriever.retrieve(
            query=message_in.content,
            top_k=5,
        )

        # ------------------------------------------------------
        # 6. Build document context for agent
        # ------------------------------------------------------

        context_parts = []

        for index, document in enumerate(
            documents,
            start=1,
        ):

            metadata = document.metadata or {}

            document_id = metadata.get(
                "document_id",
                "unknown",
            )

            filename = metadata.get(
                "filename",
                metadata.get(
                    "source",
                    "Unknown document",
                ),
            )

            page = metadata.get("page")

            if page is not None:
                try:
                    page = int(page) + 1
                except (TypeError, ValueError):
                    pass

                location = (
                    f"{filename}, page {page}"
                )
            else:
                location = filename

            context_parts.append(
                f"[Retrieved Document {index}]\n"
                f"Document ID: {document_id}\n"
                f"Filename: {filename}\n"
                f"Location: {location}\n"
                f"Content:\n"
                f"{document.page_content.strip()}"
            )

        context = "\n\n".join(
            context_parts
        )

        if not context:
            context = (
                "No relevant documents were retrieved."
            )
        # ------------------------------------------------------
        # 7. Find document(s) tool
        # ------------------------------------------------------
        find_documents_tool = create_find_document_tool(db=self.db)

        # ------------------------------------------------------
        # 7. Create authorized email tool
        # ------------------------------------------------------

        document_email_tool = (create_document_email_tool(
                db=self.db,
                user_name=user_name,
                recipient_email=user_email,
            )
        )

        # ------------------------------------------------------
        # 8. Build agent with tools
        # ------------------------------------------------------

        agent = build_agent(
            tools=[
                find_documents_tool,
                document_email_tool,
            ]
        )

        # ------------------------------------------------------
        # 9. Run agent
        # ------------------------------------------------------

        result = await agent.ainvoke(
            {
                "input": message_in.content,
                "context": context,
                "chat_history": history,
                "user_context": (
                    f"Authenticated user: {user_name}\n"
                    f"Email: {user_email}\n"
                    f"User ID: {user_id}"
                ),
            }
        )

        answer = result.get(
            "output",
            "I was unable to generate a response.",
        )

        # ------------------------------------------------------
        # 10. Save assistant response
        # ------------------------------------------------------

        return self.create_assistant_message(
            chat_id=chat_id,
            user_id=user_id,
            content=answer,
        )

    # ==========================================================
    # LIST MESSAGES
    # ==========================================================

    def list_messages(
        self,
        chat_id: int,
        user_id: int,
    ) -> list[ChatMessage]:

        chat = (
            self.db.query(Chat)
            .filter(
                Chat.id == chat_id,
                Chat.user_id == user_id,
            )
            .first()
        )

        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found",
            )

        return (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.chat_id == chat_id
            )
            .order_by(
                ChatMessage.created_at.asc()
            )
            .all()
        )