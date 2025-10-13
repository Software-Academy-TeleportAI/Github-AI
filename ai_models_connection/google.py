from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from ai_models_connection.ai_provider import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    def __init__(self, credentials_json: str):
        credentials_info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self.model = "gemini-2.0-flash"
        self.credentials = credentials

    def get_llm(self):
        return ChatGoogleGenerativeAI(model=self.model, credentials=self.credentials)
