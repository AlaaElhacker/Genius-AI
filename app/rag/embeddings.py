from abc import ABC, abstractmethod

from langchain_core.embeddings import Embeddings

from app.core.config import Settings
from app.core.exceptions import ServiceError, ValidationError


class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass


class CohereEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValidationError("COHERE_API_KEY is required for Cohere embeddings.")
        self.api_key = api_key

    def get_embeddings(self) -> Embeddings:
        from langchain_cohere import CohereEmbeddings

        return CohereEmbeddings(
            cohere_api_key=self.api_key,
            model="embed-english-v3.0",
        )


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "cohere":
        return CohereEmbeddingProvider(settings.cohere_api_key)
    raise ValidationError(f"Unsupported embedding provider: {provider}")
