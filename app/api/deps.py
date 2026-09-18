from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.documents.indexer import DocumentIndexService
from app.documents.service import build_registry, build_storage
from app.llm.manager import LLMManager
from app.rag.chain import RAGService
from app.rag.embeddings import build_embedding_provider
from app.rag.vectorstore import VectorStoreService


@dataclass
class AppServices:
    settings: Settings
    document_service: DocumentIndexService
    rag_service: RAGService


_services: AppServices | None = None


def init_services(settings: Settings | None = None) -> AppServices:
    global _services
    settings = settings or get_settings()

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    settings.registry_path.parent.mkdir(parents=True, exist_ok=True)

    registry = build_registry(settings)
    storage = build_storage(settings)
    embedding_provider = build_embedding_provider(settings)
    vectorstore_service = VectorStoreService(settings, embedding_provider.get_embeddings())
    llm_manager = LLMManager(settings)

    document_service = DocumentIndexService(
        settings=settings,
        registry=registry,
        storage=storage,
        vectorstore_service=vectorstore_service,
    )
    rag_service = RAGService(
        vectorstore_service=vectorstore_service,
        llm_manager=llm_manager,
    )

    _services = AppServices(
        settings=settings,
        document_service=document_service,
        rag_service=rag_service,
    )
    return _services


def get_services() -> AppServices:
    if _services is None:
        return init_services()
    return _services
