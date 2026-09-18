import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.exceptions import QuotaError, ServiceError, ValidationError
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValidationError("GEMINI_API_KEY is required for Gemini.")
        self._llm = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=api_key,
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
            content = response.content
            if isinstance(content, list):
                return "".join(
                    block.get("text", "") if isinstance(block, dict) else str(block)
                    for block in content
                )
            return str(content)
        except Exception as exc:
            raise _map_gemini_error(exc) from exc


def _map_gemini_error(exc: Exception) -> Exception:
    message = str(exc).lower()
    if any(token in message for token in ("quota", "rate limit", "429", "resource exhausted")):
        return QuotaError("Gemini quota or rate limit exceeded.")
    if any(token in message for token in ("503", "unavailable", "timeout", "temporarily")):
        return ServiceError("Gemini is temporarily unavailable.")
    logger.exception("Gemini provider error")
    return ServiceError("Failed to generate a response with Gemini.")
