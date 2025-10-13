from langchain.chat_models import ChatOpenAI
from ai-provider import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model

    def get_llm(self):
        return ChatOpenAI(model_name=self.model, openai_api_key=self.api_key)
