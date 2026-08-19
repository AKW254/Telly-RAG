from pathlib import Path
from typing import List

from langchain_core.documents import Document as LangchainDocument
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



from app.config.settings import settings

class DocumentIndexer:
    def __init__(self):

        # ----------------------------------------------
        # Embedding model
        # ----------------------------------------------

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

        # ----------------------------------------------
        # Chroma persistence directory
        # ----------------------------------------------

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

    # ==================================================
    # Get Vector Store
    # ==================================================

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

    # ==================================================
    # Index Documents
    # ==================================================

    def index(
        self,
        documents: List[LangchainDocument],
        document_id: int,
        user_id: int,
    ) -> int:

        if not documents:
            return 0

        # ----------------------------------------------
        # Add metadata
        # ----------------------------------------------

        for document in documents:

            document.metadata.update(
                {
                    "document_id": str(document_id),
                    "user_id": str(user_id),
                }
            )

        # ----------------------------------------------
        # Vector store
        # ----------------------------------------------

        vector_store = self.get_vector_store()

        # ----------------------------------------------
        # Generate IDs
        # ----------------------------------------------

        ids = [
            f"document-{document_id}-chunk-{index}"
            for index in range(len(documents))
        ]

        # ----------------------------------------------
        # Store documents + embeddings
        # ----------------------------------------------

        vector_store.add_documents(
            documents=documents,
            ids=ids,
        )

        return len(documents)

    # ==================================================
    # Remove a document's vectors
    # ==================================================

    def delete_document_embeddings(
        self,
        document_id: int,
        user_id: int | None = None,
    ) -> None:
        """Delete every chunk belonging to one application document.

        Chroma metadata is stored as strings, so the filter must use the
        string representation of the identifiers.
        """

        # Document primary keys are globally unique, so this one condition
        # also avoids Chroma's single-expression metadata filter limitation.
        where = {"document_id": str(document_id)}

        vector_store = self.get_vector_store()
        vector_store._collection.delete(where=where)
