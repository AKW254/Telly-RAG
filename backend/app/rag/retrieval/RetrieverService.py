from functools import lru_cache
from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings



class RetrieverService:
    def __init__(self,collection_name: str = "telly_documents",):
        self._embeddings = None
        self._vector_store = None
        self.collection_name = collection_name
        self.persist_directory = Path(getattr(settings,"chroma_persist_directory","storage/chroma",))
        self.persist_directory.mkdir(parents=True, exist_ok=True,)

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

        return self._embeddings

    @property
    def vector_store(self):
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )

        return self._vector_store

    # ======================================================
    # Retrieve
    # ======================================================

    def retrieve(self,query: str,top_k: int = 5,) -> List[Document]:

        if not query.strip():
            return []

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        results = self.vector_store.similarity_search(query=query, k=top_k)

        return results


@lru_cache(maxsize=1)
def get_retriever() -> RetrieverService:
    return RetrieverService()