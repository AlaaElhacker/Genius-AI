from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

from app.core.config import Settings


class VectorStoreService:
    def __init__(
        self,
        settings: Settings,
        embeddings: Embeddings,
    ):
        self.settings = settings
        self.settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        self._vectorstore = Chroma(
            collection_name=settings.collection_name,
            embedding_function=embeddings,
            persist_directory=str(settings.chroma_dir),
        )

    @property
    def vectorstore(self) -> Chroma:
        return self._vectorstore

    def add_documents(self, documents: list[Document]) -> None:
        if documents:
            self._vectorstore.add_documents(documents)

    def delete_by_document_id(self, document_id: str) -> None:
        self._vectorstore.delete(where={"document_id": document_id})

    def as_retriever(self, document_id: str | None = None) -> VectorStoreRetriever:
        search_kwargs: dict = {"k": self.settings.top_k}
        if document_id:
            search_kwargs["filter"] = {"document_id": document_id}
        return self._vectorstore.as_retriever(search_kwargs=search_kwargs)
