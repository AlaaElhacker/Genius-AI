from langchain_core.documents import Document

from app.models.chat import Source


def build_sources(documents: list[Document]) -> list[Source]:
    seen: set[tuple[str, int | None]] = set()
    sources: list[Source] = []

    for doc in documents:
        metadata = doc.metadata
        document_id = metadata.get("document_id")
        file_name = metadata.get("file_name") or metadata.get("source", "Unknown")
        page = metadata.get("page")

        if not document_id:
            continue

        key = (document_id, page)
        if key in seen:
            continue
        seen.add(key)

        sources.append(
            Source(
                document_id=document_id,
                file_name=file_name,
                page=page,
            )
        )

    return sources
