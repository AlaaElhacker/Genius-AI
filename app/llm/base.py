from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        pass
