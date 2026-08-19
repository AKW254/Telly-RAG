from pathlib import Path

from app.celery_app import celery_app
from app.database.database import SessionLocal
from app.models.documents import Document
from app.rag.ingestion.ingestion_service import IngestionService
from app.utils.logger import logger


TASK_MAX_RETRIES = 3
TASK_RETRY_DELAY_SECONDS = 60


@celery_app.task(
    bind=True,
    name="app.tasks.process_document_task",
    max_retries=TASK_MAX_RETRIES,
    default_retry_delay=TASK_RETRY_DELAY_SECONDS,
)
def process_document_task(
    self,
    document_id: int,
    expected_file_path: str | None = None,
) -> bool:

    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            logger.error(
                "Document %s not found",
                document_id,
            )
            return False

        # A replacement upload may have superseded this queued task. Do not
        # let an older task re-index the previous file.
        if (
            expected_file_path is not None
            and document.file_path != expected_file_path
        ):
            logger.info(
                "Skipping stale ingestion task for document %s",
                document_id,
            )
            return False

        if not document.file_path:
            document.status = "failed"
            db.commit()

            logger.error(
                "Document %s has no file path",
                document_id,
            )

            return False

        file_path = Path(document.file_path)

        if not file_path.exists():
            document.status = "failed"
            db.commit()

            logger.error(
                "Document file does not exist: %s",
                file_path,
            )

            return False

        # ----------------------------------------------
        # Start processing
        # ----------------------------------------------

        document.status = "processing"
        db.commit()

        # ----------------------------------------------
        # RAG ingestion
        # ----------------------------------------------

        ingestion_service = IngestionService()

        ingestion_service.process_document(
            file_path=str(file_path),
            document_id=document.id,
            user_id=document.user_id,
        )

        # ----------------------------------------------
        # Successfully indexed
        # ----------------------------------------------

        document.status = "completed"
        db.commit()

        logger.info(
            "Document %s successfully processed",
            document_id,
        )

        return True

    except Exception as exc:

        logger.exception(
            "Document %s processing failed",
            document_id,
        )

        try:
            document = (
                db.query(Document)
                .filter(Document.id == document_id)
                .first()
            )

            if document:
                document.status = "failed"
                db.commit()

        except Exception:
            db.rollback()

        raise self.retry(exc=exc)

    finally:
        db.close()
