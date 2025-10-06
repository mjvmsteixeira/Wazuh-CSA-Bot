"""Base abstract class for AI services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator


class BaseAIService(ABC):
    """Abstract base class for AI analysis services."""

    @abstractmethod
    async def analyze_check(
        self, check_data: Dict[str, Any], language: str = "en"
    ) -> str:
        """
        Analyze an SCA check and return a formatted report.

        Args:
            check_data: Dictionary containing check information
            language: Language for the report ('pt' or 'en')

        Returns:
            Formatted analysis report as string
        """
        pass

    @abstractmethod
    async def analyze_check_stream(
        self, check_data: Dict[str, Any], language: str = "en"
    ) -> AsyncIterator[str]:
        """
        Stream analysis of an SCA check.

        Args:
            check_data: Dictionary containing check information
            language: Language for the report ('pt' or 'en')

        Yields:
            Chunks of the analysis report
        """
        pass

    def _build_prompt(self, check_data: Dict[str, Any], language: str) -> str:
        """Build the prompt for AI analysis."""
        prompts = {
            "pt": """Tarefa: Analise os seguintes dados de verificação SCA do Wazuh e forneça um relatório técnico.

O relatório deve conter:
1. **Descrição do Problema:** Explicação clara do problema de segurança.
2. **Passos de Remediação:** Passos técnicos detalhados para corrigir o problema.

Comece sua resposta imediatamente com a seguinte linha:
--- Relatório de Análise de Conformidade SCA ---

Dados da Verificação:
ID: {check_id}
Título: {title}
Justificativa: {rationale}
Remediação: {remediation}
""",
            "en": """Task: Analyze the following Wazuh SCA check data and provide a technical report.

The report must contain:
1. **Problem Description:** Clear explanation of the security issue.
2. **Remediation Steps:** Detailed technical steps to fix the problem.

Begin your response immediately with the following line:
--- SCA Compliance Analysis Report ---

Check Data:
ID: {check_id}
Title: {title}
Rationale: {rationale}
Remediation: {remediation}
""",
        }

        template = prompts.get(language, prompts["en"])
        return template.format(
            check_id=check_data.get("id", "N/A"),
            title=check_data.get("title", "N/A"),
            rationale=check_data.get("rationale", "N/A"),
            remediation=check_data.get("remediation", "N/A"),
        )
