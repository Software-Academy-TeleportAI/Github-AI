from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    @abstractmethod
    def get_llm(self):
        """Return a ready-to-use LLM object compatible with chains/pipelines."""
        pass
