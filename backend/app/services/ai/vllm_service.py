"""vLLM AI service implementation."""

from typing import Dict, Any, AsyncIterator
import httpx

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import AIServiceError
from app.services.ai.base import BaseAIService


class VLLMService(BaseAIService):
    """AI service using vLLM (OpenAI-compatible API)."""

    def __init__(self):
        self.api_url = settings.vllm_api_url
        self.model = settings.vllm_model

    async def analyze_check(
        self, check_data: Dict[str, Any], language: str = "en", agent_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze check using vLLM and return report with remediation script."""
        prompt = self._build_prompt(check_data, language, agent_info)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_url}/completions",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "max_tokens": 3072,  # Increased for script generation
                        "temperature": 0.1,
                        "stop": ["User:", "Check Data:", "End of Report"],
                    },
                )
                response.raise_for_status()
                result = response.json()
                report = result["choices"][0]["text"].strip()

                # Ensure report starts with header
                header = (
                    "--- Relatório de Análise de Conformidade SCA ---"
                    if language == "pt"
                    else "--- SCA Compliance Analysis Report ---"
                )
                if not report.startswith("---"):
                    report = f"{header}\n{report}"

                # Parse remediation script from the report
                os_info = agent_info.get("os") if agent_info else None
                script_data = self._parse_remediation_script(report, os_info)

                logger.info(
                    f"vLLM analysis completed for check {check_data.get('id')}"
                    + (f" with script ({script_data['script_language']})" if script_data else " (no script)")
                )

                return {
                    "report": report,
                    "remediation_script": script_data
                }

        except Exception as e:
            logger.error(f"vLLM analysis failed: {e}")
            raise AIServiceError(f"vLLM analysis failed: {str(e)}")

    async def analyze_check_stream(
        self, check_data: Dict[str, Any], language: str = "en", agent_info: Dict[str, Any] = None
    ) -> AsyncIterator[str]:
        """Stream analysis using vLLM."""
        prompt = self._build_prompt(check_data, language, agent_info)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/completions",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "max_tokens": 2048,
                        "temperature": 0.1,
                        "stream": True,
                        "stop": ["User:", "Check Data:", "End of Report"],
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json

                                chunk = json.loads(data)
                                if text := chunk["choices"][0].get("text"):
                                    yield text
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"vLLM streaming failed: {e}")
            raise AIServiceError(f"vLLM streaming failed: {str(e)}")
