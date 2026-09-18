import hashlib
import json
import re
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.documents import DocumentRecord


def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def sanitize_filename(filename: str) -> str:
    if not filename:
        raise ValidationError("Filename is required.")

    name = Path(filename).name
    if ".." in name or name.startswith("."):
        raise ValidationError("Invalid filename.")

    name = re.sub(r"[^\w\s\-.]", "", name, flags=re.UNICODE)
    name = name.strip().replace(" ", "_")

    if not name.lower().endswith(".pdf"):
        name = f"{name}.pdf"

    if name in ("", ".pdf"):
        raise ValidationError("Invalid filename.")

    return name


class DocumentRegistry:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_path.exists():
            self._save({})

    def _load(self) -> dict[str, dict]:
        if not self.registry_path.exists():
            return {}
        with open(self.registry_path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: dict[str, dict]) -> None:
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get(self, document_id: str) -> DocumentRecord | None:
        data = self._load()
        record = data.get(document_id)
        return DocumentRecord(**record) if record else None

    def get_by_hash(self, file_hash: str) -> DocumentRecord | None:
        for record in self._load().values():
            if record["file_hash"] == file_hash:
                return DocumentRecord(**record)
        return None

    def list_all(self) -> list[DocumentRecord]:
        return [DocumentRecord(**r) for r in self._load().values()]

    def add(self, record: DocumentRecord) -> None:
        data = self._load()
        data[record.document_id] = record.model_dump()
        self._save(data)

    def delete(self, document_id: str) -> DocumentRecord:
        data = self._load()
        if document_id not in data:
            raise NotFoundError("Document not found.")
        record = DocumentRecord(**data.pop(document_id))
        self._save(data)
        return record


class DocumentStorage:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save(self, document_id: str, file_bytes: bytes) -> Path:
        path = self.upload_dir / f"{document_id}.pdf"
        path.write_bytes(file_bytes)
        return path

    def get_path(self, document_id: str) -> Path:
        path = self.upload_dir / f"{document_id}.pdf"
        if not path.exists():
            raise NotFoundError("Document file not found.")
        return path

    def delete(self, document_id: str) -> None:
        path = self.upload_dir / f"{document_id}.pdf"
        if path.exists():
            path.unlink()


def validate_pdf(file_bytes: bytes, max_bytes: int) -> None:
    if len(file_bytes) == 0:
        raise ValidationError("Uploaded file is empty.")

    if len(file_bytes) > max_bytes:
        raise ValidationError(f"File exceeds maximum size of {max_bytes // (1024 * 1024)} MB.")

    if not file_bytes.startswith(b"%PDF-"):
        raise ValidationError("Invalid PDF file.")


def build_registry(settings: Settings) -> DocumentRegistry:
    return DocumentRegistry(settings.registry_path)


def build_storage(settings: Settings) -> DocumentStorage:
    return DocumentStorage(settings.upload_dir)
