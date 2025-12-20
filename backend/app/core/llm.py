import os
from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
from langchain_core.language_models.chat_models import BaseChatModel

class LLMFactory:
    @staticmethod
    def get_llm(provider: str = "google", model_name: str = None) -> BaseChatModel:
        """
        Factory to get the LLM instance based on provider.
        Default is Google Vertex AI (Gemini 1.5 Flash).
        """
        if provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
            
            # Default to Claude 3.5 Sonnet if not specified
            # Using the latest stable model name
            model = model_name or "claude-3-5-haiku-20241022"
            return ChatAnthropic(
                model=model,
                api_key=api_key,
                temperature=0
            )
        
        elif provider == "google":
            # Vertex AI uses Application Default Credentials (ADC)
            # Ensure you have run `gcloud auth application-default login`
            # or set GOOGLE_APPLICATION_CREDENTIALS
            
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
            
            model = model_name or "gemini-2.5-flash"
            
            return ChatVertexAI(
                model_name=model,
                project=project_id,
                location=location,
                temperature=0
            )
            
        raise ValueError(f"Unsupported LLM provider: {provider}")
