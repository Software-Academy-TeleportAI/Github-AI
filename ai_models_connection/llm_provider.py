from typing import Optional
import json
from ai_models_connection.ai_provider import BaseLLMProvider
from ai_models_connection.openai import OpenAIProvider
from ai_models_connection.claude import ClaudeProvider
from ai_models_connection.google import GoogleProvider


class LLMProviderFactory:
    @staticmethod
    def create_provider(provider_name: str, credentials: dict | str = None, model: str= None, api_key: str = None, temperature = 0) -> Optional[BaseLLMProvider]:
        """Returnează providerul corespunzător în funcție de alegerea user-ului."""
        # if isinstance(credentials, str):
        #     credentials = credentials.strip()
        #     # Only parse JSON if it looks like a JSON object
        #     if credentials.startswith("{") and credentials.endswith("}"):
        #         try:
        #             credentials = json.loads(credentials)
        #         except json.JSONDecodeError:
        #             raise ValueError("Invalid credentials JSON string")

        provider_name = provider_name.lower().strip()

        if provider_name == "openai":
            return OpenAIProvider(api_key=api_key, model=model, temperature=temperature)

        elif provider_name == "claude":
            return ClaudeProvider(api_key=api_key, model=model, temperature=temperature)

        elif provider_name == "google":
            return GoogleProvider(api_key=api_key, model=model, temperature=temperature)

        else:
            raise ValueError(f"Unsupported provider '{provider_name}'")
