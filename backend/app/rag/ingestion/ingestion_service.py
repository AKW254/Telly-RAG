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
        
    # ==================================================
    # Process Document
    # ==================================================
    def process_document(
        self,
        file_path: str,
        document_id: int,
        user_id: int,
        replace_existing: bool = True,
    ):
       
        # indexing fails, stale content must not remain available to retrieval.
        if replace_existing:
            self.indexer.delete_document_embeddings(
                document_id=document_id,
                user_id=user_id,
            )

        #Get the file extension
        extension = Path(file_path).suffix.lower()
        
        
        # ----------------------------------------------
        # Select loader
        # ----------------------------------------------

        if extension == ".pdf":

            loader = PdfLoader(
                file_path
            )

        elif extension == ".docx":

            loader = DocxLoader(
                file_path
            )
       
        elif extension in {".txt", ".md"}:
        
            loader = TextLoader(file_path)

        else:

            raise ValueError(
                f"Unsupported document type: {extension}"
            )
        
        # ----------------------------------------------
        # Load document
        # ----------------------------------------------

        documents = loader.load()

        if not documents:
            raise ValueError(
                "No content could be extracted from document"
            ) 
        
        # ----------------------------------------------
        # Split document
        # ----------------------------------------------

        chunks = self.text_splitter.split(
            documents
        )

        if not chunks:
            raise ValueError(
                "Document produced no chunks"
            )
            
        # ----------------------------------------------
        # Index into Chroma
        # ----------------------------------------------

        chunk_count = self.indexer.index(
            documents=chunks,
            document_id=document_id,
            user_id=user_id,
        )

        return {
            "document_id": document_id,
            "chunk_count": chunk_count,
            "status": "completed",
        }           
