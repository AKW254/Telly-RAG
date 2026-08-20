from langchain_core.documents import Document

from app.llm.llm import get_llm
from app.rag.generation.prompts.rag_prompt import RAG_PROMPT


class GeneratorService:

    def __init__(self):
        self.llm = get_llm()

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

            source = metadata.get(
                "source",
                metadata.get(
                    "filename",
                    "Unknown source",
                ),
            )

            page = metadata.get("page")

            if page is not None:
                try:
                    page = int(page) + 1
                except (TypeError, ValueError):
                    pass

                source = f"{source}, page {page}"

            sections.append(
                f"[Source {index}: {source}]\n"
                f"{document.page_content.strip()}"
            )

        return "\n\n".join(sections)

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

    async def generate(
        self,
        question: str,
        documents: list[Document],
        chat_history: list[dict],
    ) -> str:

        prompt = RAG_PROMPT.invoke(
            {
                "context": self.format_documents(documents),
                "chat_history": self.format_history(
                    chat_history
                ),
                "question": question,
            }
        )

        response = await self.llm.ainvoke(prompt)

        return str(response.content).strip()