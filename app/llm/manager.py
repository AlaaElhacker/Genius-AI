import logging

from app.core.config import Settings
from app.core.exceptions import QuotaError, ServiceError, ValidationError
from app.llm.base import LLMProvider
from app.llm.cohere import CohereProvider
from app.llm.gemini import GeminiProvider

logger = logging.getLogger(__name__)


class LLMManager:
    def __init__(self, settings: Settings):
        self.primary = _build_provider(settings.primary_llm, settings)
        fallback_name = settings.fallback_llm.lower().strip()
        self.fallback: LLMProvider | None = None
        if fallback_name and fallback_name != settings.primary_llm.lower():
            try:
                self.fallback = _build_provider(fallback_name, settings)
            except ValidationError:
                logger.warning("Fallback LLM provider is not configured.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            return self.primary.invoke(system_prompt, user_prompt)
        except (QuotaError, ServiceError) as exc:
            if self.fallback is None:
                raise
            logger.warning(
                "Primary LLM failed (%s). Falling back to %s.",
                exc.message,
                self.fallback.name,
            )
            return self.fallback.invoke(system_prompt, user_prompt)


def _build_provider(name: str, settings: Settings) -> LLMProvider:
    provider_name = name.lower().strip()
    if provider_name == "gemini":
        return GeminiProvider(settings.gemini_api_key)
    if provider_name == "cohere":
        return CohereProvider(settings.cohere_api_key)
    raise ValidationError(f"Unsupported LLM provider: {name}")
