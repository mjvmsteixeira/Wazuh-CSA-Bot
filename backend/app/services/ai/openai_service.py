"""OpenAI AI service implementation."""

from typing import Dict, Any, AsyncIterator
from openai import AsyncOpenAI

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import AIServiceError
from app.services.ai.base import BaseAIService


class OpenAIService(BaseAIService):
    """AI service using OpenAI API (ChatGPT)."""

    def __init__(self):
        if not settings.openai_api_key:
            raise AIServiceError("OpenAI API key not configured")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.model = settings.openai_model

    async def analyze_check(
        self, check_data: Dict[str, Any], language: str = "en"
    ) -> str:
        """Analyze check using OpenAI."""
        prompt = self._build_prompt(check_data, language)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert specialized in analyzing security configuration assessments.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2048,
            )

            report = response.choices[0].message.content.strip()

            # Ensure report starts with header
            header = (
                "--- Relatório de Análise de Conformidade SCA ---"
                if language == "pt"
                else "--- SCA Compliance Analysis Report ---"
            )
            if not report.startswith("---"):
                report = f"{header}\n{report}"

            logger.info(
                f"OpenAI analysis completed for check {check_data.get('id')}"
            )
            return report

        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            raise AIServiceError(f"OpenAI analysis failed: {str(e)}")

    async def analyze_check_stream(
        self, check_data: Dict[str, Any], language: str = "en"
    ) -> AsyncIterator[str]:
        """Stream analysis using OpenAI."""
        prompt = self._build_prompt(check_data, language)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert specialized in analyzing security configuration assessments.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2048,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise AIServiceError(f"OpenAI streaming failed: {str(e)}")
