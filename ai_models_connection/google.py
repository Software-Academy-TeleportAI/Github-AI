# from google.oauth2 import service_account
# from langchain_google_genai import ChatGoogleGenerativeAI
# import json
# from ai_models_connection.ai_provider import BaseLLMProvider


# class GoogleProvider(BaseLLMProvider):
#     def __init__(self, credentials_json: str, model: str = "gemini-2.0-flash"):
#         credentials_info = json.loads(credentials_json)
#         credentials = service_account.Credentials.from_service_account_info(credentials_info)
#         self.model = model
#         self.credentials = credentials

#     def get_llm(self):
#         return ChatGoogleGenerativeAI(model=self.model, credentials=self.credentials)


# In ai_models_connection/google.py

from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from ai_models_connection.ai_provider import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
 
    def __init__(self, credentials: str | dict = None, model: str = "gemini-2.0-flash", api_key: str = None, temperature: float = 0.1):
        self.model = model
        self.api_key = None
        self.credentials = None
        self.temperature = temperature 

        if isinstance(credentials, dict):
            credentials_info = credentials
            self.credentials = service_account.Credentials.from_service_account_info(credentials_info)
            
        elif isinstance(api_key, str):
            self.api_key = api_key
  

        else:
            raise ValueError("Credentials must be a dictionary (Service Account JSON) or a string (API Key).")


    def get_llm(self):
      
        return ChatGoogleGenerativeAI(
            model=self.model,
            credentials=self.credentials,
            google_api_key=self.api_key,
            temperature=self.temperature
    )