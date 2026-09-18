import logging
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import DuplicateError, ServiceError, ValidationError
from app.documents.service import (
    DocumentRegistry,
    DocumentStorage,
    compute_file_hash,
    sanitize_filename,
    validate_pdf,
)
from app.models.documents import DocumentRecord, UploadResponse
from app.rag.pipeline import enrich_chunks, load_pdf, split_documents
from app.rag.vectorstore import VectorStoreService

logger = logging.getLogger(__name__)


class DocumentIndexService:
    def __init__(
        self,
        settings: Settings,
        registry: DocumentRegistry,
        storage: DocumentStorage,
        vectorstore_service: VectorStoreService,
    ):
        self.settings = settings
        self.registry = registry
        self.storage = storage
        self.vectorstore_service = vectorstore_service

    def index_upload(self, filename: str, file_bytes: bytes) -> UploadResponse:
        validate_pdf(file_bytes, self.settings.max_upload_bytes)
        safe_name = sanitize_filename(filename)
        file_hash = compute_file_hash(file_bytes)
        document_id = file_hash

        existing = self.registry.get_by_hash(file_hash)
        if existing:
            return UploadResponse(
                document=existing,
                status="already_indexed",
                message="This document is already in your research library.",
            )

        self.storage.save(document_id, file_bytes)
        pdf_path = self.storage.get_path(document_id)

        try:
            pages = load_pdf(str(pdf_path))
            if not pages:
                raise ValidationError("PDF contains no readable text.")

            chunks = split_documents(pages, self.settings)
            if not chunks:
                raise ValidationError("Unable to create text chunks from the PDF.")

            enriched = enrich_chunks(
                chunks,
                document_id=document_id,
                file_name=safe_name,
                file_hash=file_hash,
            )

            self.vectorstore_service.add_documents(enriched)

            record = DocumentRecord(
                document_id=document_id,
                file_name=safe_name,
                file_hash=file_hash,
                page_count=len(pages),
                chunk_count=len(enriched),
            )
            self.registry.add(record)

            return UploadResponse(document=record)
        except ValidationError:
            self.storage.delete(document_id)
            raise
        except Exception as exc:
            self.storage.delete(document_id)
            logger.exception("Failed to index document")
            raise ServiceError("Failed to index the uploaded PDF.") from exc

    def list_documents(self) -> list[DocumentRecord]:
        return self.registry.list_all()

    def get_document(self, document_id: str) -> DocumentRecord:
        record = self.registry.get(document_id)
        if not record:
            from app.core.exceptions import NotFoundError

            raise NotFoundError("Document not found.")
        return record

    def get_file_path(self, document_id: str) -> Path:
        self.get_document(document_id)
        return self.storage.get_path(document_id)

    def delete_document(self, document_id: str) -> DocumentRecord:
        record = self.registry.delete(document_id)
        self.vectorstore_service.delete_by_document_id(document_id)
        self.storage.delete(document_id)
        return record
