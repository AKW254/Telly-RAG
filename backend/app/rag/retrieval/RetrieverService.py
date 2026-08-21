from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings



class RetrieverService:
    def __init__(self,collection_name: str = "telly_documents",):
        # ==================================================
        # Embedding Model
        # ==================================================

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
    
        self.persist_directory = Path(getattr(settings,"chroma_persist_directory","storage/chroma",))
        self.persist_directory.mkdir(parents=True, exist_ok=True,)
        # ==================================================
        # Chroma Vector Store
        # ==================================================

        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory,
        )

    # ======================================================
    # Retrieve
    # ======================================================

    def retrieve(self,query: str,top_k: int = 5,) -> List[Document]:

        if not query.strip():
            return []

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        results = self.vector_store.similarity_search(query=query,k=top_k,)

        return results