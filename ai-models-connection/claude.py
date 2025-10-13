from langchain_anthropic import ChatAnthropic
from ai-provider import BaseLLMProvider

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatAnthropic(model=self.model, api_key=self.api_key)
