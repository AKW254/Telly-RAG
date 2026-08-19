from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.users import User
from app.schemas.documents_schema import DocumentResponse
from app.services.documents_service import DocumentsService


router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:

    service = DocumentsService(db)

    return await service.create_document(
        user_id=current_user.id,
        file=file,
    )


@router.get(
    "/",
    response_model=List[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DocumentResponse]:

    service = DocumentsService(db)

    return service.list_documents(
        current_user.id
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:

    service = DocumentsService(db)

    return service.get_document(
        document_id=document_id,
        user_id=current_user.id,
    )


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def update_document(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """Replace a document source file and re-ingest its embeddings."""

    service = DocumentsService(db)
    return await service.update_document(
        document_id=document_id,
        user_id=current_user.id,
        file=file,
    )


@router.post(
    "/{document_id}/reingest",
    response_model=DocumentResponse,
)
def reingest_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """Rebuild embeddings from the currently stored document file."""

    service = DocumentsService(db)
    return service.reingest_document(
        document_id=document_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:

    service = DocumentsService(db)

    service.delete_document(
        document_id=document_id,
        user_id=current_user.id,
    )

    return None
