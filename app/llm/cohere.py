import logging

from langchain_cohere import ChatCohere

from app.core.exceptions import QuotaError, ServiceError, ValidationError
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class CohereProvider(LLMProvider):
    name = "cohere"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValidationError("COHERE_API_KEY is required for Cohere.")
        self._llm = ChatCohere(
            model="command-r-plus-08-2024",
            cohere_api_key=api_key,
            temperature=0.2,
        )

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._llm.invoke(
                [
                    ("system", system_prompt),
                    ("human", user_prompt),
                ]
            )
            return str(response.content)
        except Exception as exc:
            raise _map_cohere_error(exc) from exc


def _map_cohere_error(exc: Exception) -> Exception:
    message = str(exc).lower()
    if any(token in message for token in ("quota", "rate limit", "429", "too many requests")):
        return QuotaError("Cohere quota or rate limit exceeded.")
    if any(token in message for token in ("503", "unavailable", "timeout", "temporarily")):
        return ServiceError("Cohere is temporarily unavailable.")
    logger.exception("Cohere provider error")
    return ServiceError("Failed to generate a response with Cohere.")
