"""LLM client abstract interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    @property
    def usage(self):
        return type("Usage", (), {"total_tokens": self.total_tokens})()


class LLMClient(ABC):
    """LLM client abstract base class"""

    @abstractmethod
    def complete(
        self,
        message: str,
        system_message: str = "You are a helpful assistant.",
        temperature: float = 0.8,
        max_tokens: int = 8192,
    ) -> Tuple[str, LLMResponse]:
        """
        Get model response
        Returns:
            (response_content, usage_info)
        """
        pass
