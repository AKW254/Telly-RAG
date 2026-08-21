from pathlib import Path

from app.rag.ingestion.loaders.docx_loader import DocxLoader
from app.rag.ingestion.loaders.pdf_loader import PdfLoader
from app.rag.ingestion.loaders.text_loader import TextLoader
from app.rag.ingestion.indexer import DocumentIndexer
from app.rag.ingestion.splitters.text_splitter import TextSplitter


class IngestionService:

    def __init__(self):

        self.indexer = DocumentIndexer()
        self.text_splitter = TextSplitter()

    # ======================================================
    # Process Document
    # ======================================================

    def process_document(
        self,
        file_path: str,
        document_id: int,
        filename: str,
        user_id: int | None = None,
        replace_existing: bool = True,
    ):

        # --------------------------------------------------
        # Validate file
        # --------------------------------------------------

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document does not exist: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Document path is not a file: {file_path}"
            )

        # --------------------------------------------------
        # Extension
        # --------------------------------------------------

        extension = path.suffix.lower()

        # --------------------------------------------------
        # Loader
        # --------------------------------------------------

        if extension == ".pdf":

            loader = PdfLoader(file_path)

        elif extension == ".docx":

            loader = DocxLoader(file_path)

        elif extension in {".txt", ".md"}:

            loader = TextLoader(file_path)

        else:

            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        # --------------------------------------------------
        # Load
        # --------------------------------------------------

        documents = loader.load()

        if not documents:
            raise ValueError(
                "No content could be extracted from document"
            )

        # --------------------------------------------------
        # Split
        # --------------------------------------------------

        chunks = self.text_splitter.split(documents)

        if not chunks:
            raise ValueError(
                "Document produced no chunks"
            )

        # --------------------------------------------------
        # Replace existing vectors
        # --------------------------------------------------

        if replace_existing:

            self.indexer.delete_document_embeddings(
                document_id=document_id,
            )

        # --------------------------------------------------
        # Index
        # --------------------------------------------------

        chunk_count = self.indexer.index(
            documents=chunks,
            document_id=document_id,
            filename=filename,
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "chunk_count": chunk_count,
            "status": "completed",
        }