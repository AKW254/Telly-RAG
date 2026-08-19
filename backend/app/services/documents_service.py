from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.documents import Document
from app.rag.ingestion.ingestion_service import IngestionService
from app.tasks.document_tasks import process_document_task


class DocumentsService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".txt",
        ".md",
        ".docx",
    }

    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    DEFAULT_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self, db: Session):
        self.db = db

    # ==================================================
    # Create / Upload Document
    # ==================================================

    async def create_document(
        self,
        user_id: int,
        file: UploadFile,
    ) -> Document:

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required",
            )

        # ----------------------------------------------
        # File extension
        # ----------------------------------------------

        original_filename = Path(file.filename)
        extension = original_filename.suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported file type '{extension}'. "
                    "Allowed types: PDF, DOCX, TXT and MD."
                ),
            )

        # ----------------------------------------------
        # MIME type
        # ----------------------------------------------

        mime_type = file.content_type

        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported MIME type: {mime_type}",
            )

        # ----------------------------------------------
        # Read file
        # ----------------------------------------------

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        # ----------------------------------------------
        # File size
        # ----------------------------------------------

        max_file_size = getattr(
            settings,
            "max_document_size",
            self.DEFAULT_MAX_FILE_SIZE,
        )

        if len(contents) > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=(
                    f"File exceeds the maximum allowed size "
                    f"of {max_file_size // (1024 * 1024)} MB."
                ),
            )

        # ----------------------------------------------
        # Upload directory
        # ----------------------------------------------

        upload_directory = Path(
            getattr(
                settings,
                "document_upload_dir",
                "storage/documents",
            )
        )

        upload_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ----------------------------------------------
        # Generate unique stored filename
        # ----------------------------------------------

        stored_filename = f"{uuid4()}{extension}"

        file_path = upload_directory / stored_filename

        file_path.write_bytes(contents)

        # ----------------------------------------------
        # Create DB record
        # ----------------------------------------------

        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=str(file_path),
            file_type=extension.lstrip("."),
            mime_type=mime_type,
            status="pending",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        # ----------------------------------------------
        # Queue RAG processing
        # ----------------------------------------------

        process_document_task.delay(
            document.id,
            document.file_path,
        )

        return document

    # ==================================================
    # List User Documents
    # ==================================================

    def list_documents(
        self,
        user_id: int,
    ) -> list[Document]:

        return (
            self.db.query(Document)
            .filter(
                Document.user_id == user_id
            )
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

    # ==================================================
    # Get Document
    # ==================================================

    def get_document(
        self,
        document_id: int,
        user_id: int,
    ) -> Document:

        document = (
            self.db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return document

    # ==================================================
    # Update Document
    # ==================================================

    async def update_document(
        self,
        document_id: int,
        user_id: int,
        file: UploadFile,
    ) -> Document:
        """Replace the source file and queue a clean re-ingestion."""

        document = self.get_document(
            document_id=document_id,
            user_id=user_id,
        )

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required",
            )

        original_filename = Path(file.filename)
        extension = original_filename.suffix.lower()
        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed types: PDF, DOCX, TXT and MD.",
            )

        mime_type = file.content_type
        if mime_type and mime_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported MIME type: {mime_type}",
            )

        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        max_file_size = getattr(
            settings,
            "max_document_size",
            self.DEFAULT_MAX_FILE_SIZE,
        )
        if len(contents) > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds the maximum allowed size of {max_file_size // (1024 * 1024)} MB.",
            )

        upload_directory = Path(
            getattr(settings, "document_upload_dir", "storage/documents")
        )
        upload_directory.mkdir(parents=True, exist_ok=True)
        new_file_path = upload_directory / f"{uuid4()}{extension}"
        new_file_path.write_bytes(contents)

        previous_file_path = document.file_path
        document.filename = file.filename
        document.file_path = str(new_file_path)
        document.file_type = extension.lstrip(".")
        document.mime_type = mime_type
        document.status = "pending"

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            new_file_path.unlink(missing_ok=True)
            raise

        # The task removes this document's old chunks before it indexes the
        # replacement, so only the latest upload is retrievable.
        process_document_task.delay(document.id, document.file_path)

        if previous_file_path and previous_file_path != document.file_path:
            Path(previous_file_path).unlink(missing_ok=True)

        return document

    def reingest_document(
        self,
        document_id: int,
        user_id: int,
    ) -> Document:
        """Rebuild embeddings from the existing uploaded file."""

        document = self.get_document(document_id, user_id)
        if not document.file_path or not Path(document.file_path).is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The document source file is not available for re-ingestion",
            )

        document.status = "pending"
        self.db.commit()
        self.db.refresh(document)
        process_document_task.delay(document.id, document.file_path)
        return document

    # ==================================================
    # Delete Document
    # ==================================================

    def delete_document(
        self,
        document_id: int,
        user_id: int,
    ) -> None:

        document = self.get_document(
            document_id=document_id,
            user_id=user_id,
        )

        # ----------------------------------------------
        # Delete all Chroma chunks before removing the document record. This
        # prevents deleted documents from still being returned by retrieval.
        # ----------------------------------------------

        IngestionService().indexer.delete_document_embeddings(
            document_id=document.id,
            user_id=document.user_id,
        )

        # ----------------------------------------------
        # Delete physical file
        # ----------------------------------------------

        if document.file_path:
            file_path = Path(document.file_path)

            if file_path.exists():
                file_path.unlink()

        # ----------------------------------------------
        # Delete database record
        # ----------------------------------------------

        self.db.delete(document)
        self.db.commit()
