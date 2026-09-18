from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse

from app.api.deps import AppServices, get_services
from app.models.documents import DeleteResponse, DocumentListResponse, UploadResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    services: AppServices = Depends(get_services),
) -> UploadResponse:
    if not file.filename:
        from app.core.exceptions import ValidationError

        raise ValidationError("No file provided.")

    file_bytes = await file.read()
    return services.document_service.index_upload(file.filename, file_bytes)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    services: AppServices = Depends(get_services),
) -> DocumentListResponse:
    return DocumentListResponse(documents=services.document_service.list_documents())


@router.get("/{document_id}/file")
def get_document_file(
    document_id: str,
    services: AppServices = Depends(get_services),
) -> FileResponse:
    path = services.document_service.get_file_path(document_id)
    record = services.document_service.get_document(document_id)
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=record.file_name,
    )


@router.delete("/{document_id}", response_model=DeleteResponse)
def delete_document(
    document_id: str,
    services: AppServices = Depends(get_services),
) -> DeleteResponse:
    services.document_service.delete_document(document_id)
    return DeleteResponse(document_id=document_id)
