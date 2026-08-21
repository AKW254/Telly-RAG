from langchain_core.documents import Document

from app.llm.llm import get_llm
from app.rag.generation.prompts.rag_prompt import RAG_PROMPT


class GeneratorService:

    def __init__(self):

        self.llm = get_llm()

    # ======================================================
    # Format Documents
    # ======================================================

    @staticmethod
    def format_documents(
        documents: list[Document],
    ) -> str:

        if not documents:
            return "No relevant documents were retrieved."

        sections = []

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
                    "Unknown source",
                ),
            )

            page = metadata.get("page")

            if page is not None:

                try:
                    page = int(page) + 1

                except (TypeError, ValueError):
                    pass

            page_info = ""

            if page is not None:
                page_info = f"\npage: {page}"

            sections.append(
                f"[Document {index}]\n"
                f"document_id: {document_id}\n"
                f"filename: {filename}"
                f"{page_info}\n"
                f"content:\n"
                f"{document.page_content.strip()}"
            )

        return "\n\n".join(sections)

    # ======================================================
    # Format History
    # ======================================================

    @staticmethod
    def format_history(
        history: list[dict],
    ) -> str:

        if not history:
            return "No previous conversation."

        return "\n".join(
            f"{message.get('role', 'user').capitalize()}: "
            f"{message.get('content', '')}"
            for message in history
            if message.get("content")
        )

    # ======================================================
    # Generate
    # ======================================================

    async def generate(
        self,
        question: str,
        documents: list[Document],
        chat_history: list[dict],
    ) -> str:

        prompt = RAG_PROMPT.invoke(
            {
                "context": self.format_documents(
                    documents
                ),
                "chat_history": self.format_history(
                    chat_history
                ),
                "question": question,
            }
        )

        response = await self.llm.ainvoke(prompt)

        return str(
            response.content
        ).strip()