from pathlib import Path
from typing import List

from langchain_core.documents import Document as LangchainDocument
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings


class DocumentIndexer:

    def __init__(self):

        # --------------------------------------------------
        # Embeddings
        # --------------------------------------------------

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        # --------------------------------------------------
        # Chroma persistence
        # --------------------------------------------------

        self.persist_directory = Path(
            getattr(
                settings,
                "chroma_persist_directory",
                "storage/chroma",
            )
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ======================================================
    # Vector Store
    # ======================================================

    def get_vector_store(
        self,
        collection_name: str = "telly_documents",
    ) -> Chroma:

        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(
                self.persist_directory
            ),
        )

    # ======================================================
    # Index
    # ======================================================

    def index(
        self,
        documents: List[LangchainDocument],
        document_id: int,
        filename: str,
        user_id: int | None = None,
    ) -> int:

        if not documents:
            return 0

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        for document in documents:

            document.metadata.update(
                {
                    "document_id": str(document_id),
                    "filename": filename,
                }
            )

        # --------------------------------------------------
        # Vector store
        # --------------------------------------------------

        vector_store = self.get_vector_store()

        # --------------------------------------------------
        # Deterministic IDs
        # --------------------------------------------------

        ids = [
            f"document-{document_id}-chunk-{index}"
            for index in range(len(documents))
        ]

        # --------------------------------------------------
        # Store
        # --------------------------------------------------

        vector_store.add_documents(
            documents=documents,
            ids=ids,
        )

        return len(documents)

    # ======================================================
    # Delete Document Embeddings
    # ======================================================

    def delete_document_embeddings(
        self,
        document_id: int,
    ) -> None:

        vector_store = self.get_vector_store()

        vector_store._collection.delete(
            where={
                "document_id": str(document_id),
            }
        )