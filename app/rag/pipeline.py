from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings


def load_pdf(pdf_path: str) -> list[Document]:
    loader = PyPDFLoader(pdf_path)
    return loader.load()


def split_documents(documents: list[Document], settings: Settings) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(documents)


def enrich_chunks(
    chunks: list[Document],
    *,
    document_id: str,
    file_name: str,
    file_hash: str,
) -> list[Document]:
    enriched: list[Document] = []
    for index, chunk in enumerate(chunks):
        metadata = dict(chunk.metadata)
        metadata.update(
            {
                "document_id": document_id,
                "file_name": file_name,
                "source": file_name,
                "file_hash": file_hash,
                "chunk_index": index,
            }
        )
        page = metadata.get("page")
        if page is not None:
            metadata["page"] = int(page) + 1
        enriched.append(Document(page_content=chunk.page_content, metadata=metadata))
    return enriched
