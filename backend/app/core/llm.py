import os
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

class LLMFactory:
    @staticmethod
    def get_llm(provider: str = "anthropic", model_name: str = None) -> BaseChatModel:
        """
        Factory to get the LLM instance based on provider.
        Default is Anthropic (Claude 3 Sonnet is a good balance).
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
        
        # Future providers can be added here
        # elif provider == "openai":
        #     ...
            
        raise ValueError(f"Unsupported LLM provider: {provider}")
