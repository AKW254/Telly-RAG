from pathlib import Path

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.documents import Document


# ==========================================================
# Tool Input Schema
# ==========================================================

class DocumentEmailInput(BaseModel):
    document_id: int = Field(
        ...,
        description=(
            "The ID of the document that the authenticated "
            "user wants to receive by email."
        ),
    )


# ==========================================================
# Tool Factory
# ==========================================================

def create_document_email_tool(
    db: Session,
    user_id: int,
    recipient_email: str,
) -> StructuredTool:
    """
    Creates a document-email tool scoped to the authenticated user.

    The LLM can provide only document_id.
    user_id and recipient_email come from the application.
    """

    def send_document_by_email(
        document_id: int,
    ) -> str:
        """
        Send an authenticated user's document by email.
        """

        # --------------------------------------------------
        # Find document belonging to authenticated user
        # --------------------------------------------------

        document = (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.user_id == user_id,
            )
            .first()
        )

        if not document:
            return (
                "The requested document was not found or "
                "you do not have permission to access it."
            )

        # --------------------------------------------------
        # Check stored file path
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
            # Change this import/method to your existing mailer.
            from app.services.mailer_service import MailerService

            mailer = MailerService()

            mailer.send_document_email(
                recipient=recipient_email,
                document=document,
                file_path=str(file_path),
            )

            return (
                f"The document '{document.filename}' "
                f"was successfully sent to {recipient_email}."
            )

        except Exception as exc:
            # Do not expose internal exception details to the LLM.
            return (
                f"I was unable to send '{document.filename}' "
                "right now. Please try again later."
            )

    return StructuredTool.from_function(
        func=send_document_by_email,
        name="send_document_by_email",
        description=(
            "Send a document belonging to the authenticated user "
            "to the user's configured email address. "
            "Use this only when the user explicitly asks to "
            "receive, email, send, or download a document."
        ),
        args_schema=DocumentEmailInput,
    )