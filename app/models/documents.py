from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DocumentRecord(BaseModel):
    document_id: str
    file_name: str
    file_hash: str
    page_count: int
    chunk_count: int
    indexed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DocumentListResponse(BaseModel):
    documents: list[DocumentRecord]


class UploadResponse(BaseModel):
    document: DocumentRecord
    status: str = "indexed"
    message: str = "Document indexed successfully."


class DeleteResponse(BaseModel):
    document_id: str
    message: str = "Document removed successfully."
