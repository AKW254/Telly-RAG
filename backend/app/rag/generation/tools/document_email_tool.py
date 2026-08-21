from pathlib import Path
import logging

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.documents import Document


logger = logging.getLogger(__name__)


# ==========================================================
# Tool Input
# ==========================================================

class DocumentEmailInput(BaseModel):
    document_id: int = Field(
        ...,
        description=(
            "The internal ID of the document to send. "
            "This ID must come from the retrieved document context. "
            "Never invent a document ID."
        ),
    )


# ==========================================================
# Tool Factory
# ==========================================================

def create_document_email_tool(
    db: Session,
    user_name: str,
    recipient_email: str,
) -> StructuredTool:

    def send_document_by_email(
        document_id: int,
    ) -> str:

        # --------------------------------------------------
        # Find document
        # --------------------------------------------------

        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            return (
                "The requested document could not be found."
            )

        # --------------------------------------------------
        # Verify file path
        # --------------------------------------------------

        if not document.file_path:
            return (
                f"The document '{document.filename}' "
                "does not have an available file."
            )

        file_path = Path(document.file_path)

        if not file_path.exists():
            return (
                f"The file for '{document.filename}' "
                "is no longer available."
            )

        if not file_path.is_file():
            return (
                f"The stored path for '{document.filename}' "
                "is not a valid file."
            )

        # --------------------------------------------------
        # Send email
        # --------------------------------------------------

        try:

            from app.mailer.mailer import EmailService

            service = EmailService()

            context = {
                "user_name": user_name,
                "app_name": settings.app_name,
                "document_name": document.filename,
            }

            service.send_from_template(
                to_email=recipient_email,
                subject=(
                    f"Requested document: "
                    f"{document.filename}"
                ),
                template_name="document.html",
                context=context,
                plain_text_template="document.txt",
                attachments=[
                    str(file_path),
                ],
            )

            logger.info(
                "Document %s (%s) sent to %s",
                document.id,
                document.filename,
                recipient_email,
            )

            return (
                f"The document '{document.filename}' "
                "has been successfully sent to "
                f"{recipient_email}."
            )

        except Exception:
            logger.exception(
                "Failed to send document %s to %s",
                document.id,
                recipient_email,
            )

            return (
                f"I was unable to send "
                f"'{document.filename}' right now."
            )

    # ======================================================
    # Return LangChain Tool
    # ======================================================

    return StructuredTool.from_function(
        func=send_document_by_email,
        name="send_document_by_email",
        description=(
            "Send a publicly available document to the "
            "authenticated user's configured email address. "
            "Use this tool only when the user explicitly asks "
            "to send, email, or deliver a document. "
            "The document_id MUST come from the retrieved "
            "document context. Never invent a document_id."
        ),
        args_schema=DocumentEmailInput,
    )