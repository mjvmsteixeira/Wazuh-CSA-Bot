"""AI service factory for selecting the appropriate provider."""

from typing import Literal

from app.services.ai.base import BaseAIService
from app.services.ai.vllm_service import VLLMService
from app.services.ai.openai_service import OpenAIService
from app.utils.exceptions import AIServiceError
from app.config import settings


AIProvider = Literal["vllm", "openai"]


class AIServiceFactory:
    """Factory for creating AI service instances."""

    _services = {
        "vllm": VLLMService,
        "openai": OpenAIService,
    }

    @classmethod
    def create(cls, provider: AIProvider = "vllm") -> BaseAIService:
        """
        Create an AI service instance.

        Args:
            provider: The AI provider to use ('vllm' or 'openai')

        Returns:
            Instance of the requested AI service

        Raises:
            AIServiceError: If provider is not supported or not allowed by AI_MODE
        """
        # Validate provider against AI_MODE
        if settings.ai_mode == "local" and provider == "openai":
            raise AIServiceError(
                "OpenAI provider is not available in 'local' AI mode. "
                "Change AI_MODE to 'external' or 'mixed' in .env file."
            )

        if settings.ai_mode == "external" and provider == "vllm":
            raise AIServiceError(
                "vLLM provider is not available in 'external' AI mode. "
                "Change AI_MODE to 'local' or 'mixed' in .env file."
            )

        service_class = cls._services.get(provider)
        if not service_class:
            raise AIServiceError(
                f"Unsupported AI provider: {provider}. "
                f"Supported providers: {', '.join(cls._services.keys())}"
            )

        try:
            return service_class()
        except Exception as e:
            raise AIServiceError(f"Failed to initialize {provider} service: {str(e)}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Get list of available AI providers based on AI_MODE configuration."""
        if settings.ai_mode == "local":
            return ["vllm"]
        elif settings.ai_mode == "external":
            return ["openai"]
        else:  # mixed
            return list(cls._services.keys())
