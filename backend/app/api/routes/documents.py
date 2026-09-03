from pathlib import Path
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
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
    "/{document_id}/download",
    response_class=FileResponse,
)
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    service = DocumentsService(db)
    document = service.get_document(document_id=document_id)

    if not document.file_path or not Path(document.file_path).is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found",
        )

    return FileResponse(
        path=document.file_path,
        media_type=document.mime_type or "application/octet-stream",
        filename=document.filename,
    )


@router.get(
    "/",
    response_model=List[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
   
) -> List[DocumentResponse]:

    service = DocumentsService(db)

    return service.list_documents()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    
) -> DocumentResponse:

    service = DocumentsService(db)

    return service.get_document(
        document_id=document_id,
       
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
