import logging

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.documents import Document

logger = logging.getLogger(__name__)


class FindDocumentInput(BaseModel):
    query: str = Field(
        ...,
        description=(
            "A filename or topic the user mentioned, e.g. "
            "'company profile' or 'Q3 report.pdf'."
        ),
    )


def create_find_document_tool(db: Session) -> StructuredTool:

    def find_document(query: str) -> str:

        matches = (
            db.query(Document)
            .filter(Document.filename.ilike(f"%{query}%"))
            .limit(5)
            .all()
        )

        if not matches:
            return f"No documents found matching '{query}'."

        if len(matches) > 1:
            listing = "\n".join(
                f"- id={doc.id}: {doc.filename}" for doc in matches
            )
            return (
                f"Multiple documents match '{query}'. Ask the user "
                f"which one they mean before proceeding:\n{listing}"
            )

        doc = matches[0]
        return f"Found document_id={doc.id} for '{doc.filename}'."

    return StructuredTool.from_function(
        func=find_document,
        name="find_document",
        description=(
            "Look up a document's ID by filename or topic when the "
            "user refers to a document by name instead of an ID. "
            "Always call this BEFORE send_document_by_email if you "
            "don't already have a document_id from retrieved context."
        ),
        args_schema=FindDocumentInput,
    )