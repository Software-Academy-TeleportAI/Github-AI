from langchain.chat_models import ChatGoogleGenerativeAI
from ai-provider import BaseLLMProvider

class GoogleProvider(BaseLLMProvider):
    def __init__(self, credentials, model: str = "gemini-2.0-flash"):
        self.credentials = credentials
        self.model = model

    def get_llm(self):
        return ChatGoogleGenerativeAI(model=self.model, credentials=self.credentials)
