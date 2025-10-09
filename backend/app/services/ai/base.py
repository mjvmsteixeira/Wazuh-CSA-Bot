"""Base abstract class for AI services."""

from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator, Optional
import re


class BaseAIService(ABC):
    """Abstract base class for AI analysis services."""

    @abstractmethod
    async def analyze_check(
        self, check_data: Dict[str, Any], language: str = "en", agent_info: Dict[str, Any] = None
    ) -> str:
        """
        Analyze an SCA check and return a formatted report.

        Args:
            check_data: Dictionary containing check information
            language: Language for the report ('pt' or 'en')
            agent_info: Dictionary containing agent information (name, ip, os, etc.)

        Returns:
            Formatted analysis report as string
        """
        pass

    @abstractmethod
    async def analyze_check_stream(
        self, check_data: Dict[str, Any], language: str = "en", agent_info: Dict[str, Any] = None
    ) -> AsyncIterator[str]:
        """
        Stream analysis of an SCA check.

        Args:
            check_data: Dictionary containing check information
            language: Language for the report ('pt' or 'en')
            agent_info: Dictionary containing agent information (name, ip, os, etc.)

        Yields:
            Chunks of the analysis report
        """
        pass

    def _build_prompt(self, check_data: Dict[str, Any], language: str, agent_info: Dict[str, Any] = None) -> str:
        """Build the prompt for AI analysis with agent context."""
        # Extract compliance frameworks if available
        compliance_frameworks = []
        if check_data.get("compliance"):
            for comp in check_data["compliance"]:
                compliance_frameworks.extend(comp.keys())
        compliance_str = ", ".join(compliance_frameworks) if compliance_frameworks else "N/A"

        # Extract agent information
        agent_name = "N/A"
        agent_ip = "N/A"
        os_name = "N/A"
        os_version = "N/A"
        os_arch = "N/A"

        if agent_info:
            agent_name = agent_info.get("name", "N/A")
            agent_ip = agent_info.get("ip", "N/A")
            if agent_info.get("os"):
                os_info = agent_info["os"]
                os_name = os_info.get("name", "N/A")
                os_version = os_info.get("version", "N/A")
                os_arch = os_info.get("arch", "N/A")

        prompts = {
            "pt": """Tarefa: Analise os seguintes dados de verificação SCA do Wazuh e forneça um relatório técnico detalhado com script executável.

O relatório deve conter:
1. **Descrição do Problema:** Explicação clara do problema de segurança identificado.
2. **Contexto Técnico:** Análise dos detalhes técnicos do erro (ficheiro, comando, razão específica).
3. **Passos de Remediação:** Passos técnicos detalhados e específicos para corrigir o problema, adaptados ao sistema operativo.
4. **Script de Remediação Executável:** Script completo pronto para executar (bash para Linux, powershell para Windows).
5. **Validação:** Como verificar se a correção foi aplicada com sucesso.

Comece sua resposta imediatamente com a seguinte linha:
--- Relatório de Análise de Conformidade SCA ---

## Contexto do Sistema:
**Agente:** {agent_name}
**IP:** {agent_ip}
**Sistema Operativo:** {os_name} {os_version}
**Arquitetura:** {os_arch}

## Dados da Verificação:
**ID:** {check_id}
**Título:** {title}
**Resultado:** {result}
**Compliance:** {compliance}

**Justificativa:**
{rationale}

**Remediação Recomendada:**
{remediation}

## Detalhes Técnicos do Erro:
**Razão Específica:** {reason}
**Ficheiro Afetado:** {file}
**Diretório:** {directory}
**Processo:** {process}
**Registo:** {registry}
**Comando de Verificação:** {command}
**Condição:** {condition}

IMPORTANTE:
1. Forneça passos de remediação específicos para {os_name} {os_version} ({os_arch}).
2. Considere os detalhes técnicos fornecidos (ficheiro, comando, razão) na sua análise.
3. OBRIGATÓRIO: Inclua uma seção "## Script de Remediação Automática" com um bloco de código executável:
   - Use ```bash para sistemas Linux/Unix
   - Use ```powershell para sistemas Windows
   - Inclua shebang apropriado (#!/bin/bash ou similar)
   - Adicione verificação de privilégios (root/admin check)
   - Inclua comentários explicativos
   - Adicione tratamento de erros (set -e, verificações if/else)
   - Termine com comando de validação
4. Após o bloco de script, adicione:
   **Comando de Validação:** (comando único para verificar se a correção funcionou)
   **Riscos Potenciais:** (lista de avisos, se aplicável)
   **Tempo Estimado:** (estimativa de duração)
""",
            "en": """Task: Analyze the following Wazuh SCA check data and provide a detailed technical report with executable script.

The report must contain:
1. **Problem Description:** Clear explanation of the identified security issue.
2. **Technical Context:** Analysis of technical error details (file, command, specific reason).
3. **Remediation Steps:** Detailed and specific technical steps to fix the problem, adapted to the operating system.
4. **Executable Remediation Script:** Complete ready-to-execute script (bash for Linux, powershell for Windows).
5. **Validation:** How to verify the fix was successfully applied.

Begin your response immediately with the following line:
--- SCA Compliance Analysis Report ---

## System Context:
**Agent:** {agent_name}
**IP:** {agent_ip}
**Operating System:** {os_name} {os_version}
**Architecture:** {os_arch}

## Check Data:
**ID:** {check_id}
**Title:** {title}
**Result:** {result}
**Compliance:** {compliance}

**Rationale:**
{rationale}

**Recommended Remediation:**
{remediation}

## Technical Error Details:
**Specific Reason:** {reason}
**Affected File:** {file}
**Directory:** {directory}
**Process:** {process}
**Registry:** {registry}
**Verification Command:** {command}
**Condition:** {condition}

IMPORTANT:
1. Provide remediation steps specific to {os_name} {os_version} ({os_arch}).
2. Consider the technical details provided (file, command, reason) in your analysis.
3. REQUIRED: Include a "## Automated Remediation Script" section with an executable code block:
   - Use ```bash for Linux/Unix systems
   - Use ```powershell for Windows systems
   - Include appropriate shebang (#!/bin/bash or similar)
   - Add privilege checks (root/admin check)
   - Include explanatory comments
   - Add error handling (set -e, if/else checks)
   - End with validation command
4. After the script block, add:
   **Validation Command:** (single command to verify the fix worked)
   **Potential Risks:** (list of warnings, if applicable)
   **Estimated Time:** (duration estimate)
""",
        }

        template = prompts.get(language, prompts["en"])
        return template.format(
            # Agent context
            agent_name=agent_name,
            agent_ip=agent_ip,
            os_name=os_name,
            os_version=os_version,
            os_arch=os_arch,
            # Check data
            check_id=check_data.get("id", "N/A"),
            title=check_data.get("title", "N/A"),
            result=check_data.get("result", "failed"),
            compliance=compliance_str,
            rationale=check_data.get("rationale", "N/A"),
            remediation=check_data.get("remediation", "N/A"),
            # Technical details
            reason=check_data.get("reason", "N/A"),
            file=check_data.get("file", "N/A"),
            directory=check_data.get("directory", "N/A"),
            process=check_data.get("process", "N/A"),
            registry=check_data.get("registry", "N/A"),
            command=check_data.get("command", "N/A"),
            condition=check_data.get("condition", "N/A"),
        )

    def _parse_remediation_script(
        self, ai_output: str, os_info: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Parse remediation script from AI output.

        Args:
            ai_output: The complete AI analysis output
            os_info: Optional OS information to detect script language

        Returns:
            Dictionary with script data or None if no script found
        """
        # Detect script language based on OS or code fence
        script_language = "bash"  # default
        if os_info:
            os_name = os_info.get("name", "").lower()
            if "windows" in os_name:
                script_language = "powershell"

        # Try to find code blocks with language hints
        patterns = [
            (r'```bash\s*\n(.*?)```', "bash"),
            (r'```shell\s*\n(.*?)```', "bash"),
            (r'```sh\s*\n(.*?)```', "bash"),
            (r'```powershell\s*\n(.*?)```', "powershell"),
            (r'```ps1\s*\n(.*?)```', "powershell"),
            (r'```python\s*\n(.*?)```', "python"),
        ]

        script_content = None
        detected_language = script_language

        for pattern, lang in patterns:
            match = re.search(pattern, ai_output, re.DOTALL | re.IGNORECASE)
            if match:
                script_content = match.group(1).strip()
                detected_language = lang
                break

        if not script_content:
            # Try generic code block
            match = re.search(r'```\s*\n(.*?)```', ai_output, re.DOTALL)
            if match:
                script_content = match.group(1).strip()

        if not script_content:
            return None

        # Extract validation command
        validation_match = re.search(
            r'\*\*(?:Comando de )?Valida[çc][ãa]o(?:\s+Command)?[:\*]\*\*\s*[`]?(.*?)[`]?(?:\n|$)',
            ai_output,
            re.IGNORECASE
        )
        validation_command = validation_match.group(1).strip() if validation_match else ""

        # Extract risks
        risks = []
        risks_section = re.search(
            r'\*\*(?:Riscos )?Potenciais?(?: Risks)?[:\*]\*\*(.*?)(?:\n\*\*|\n##|$)',
            ai_output,
            re.DOTALL | re.IGNORECASE
        )
        if risks_section:
            risk_text = risks_section.group(1)
            # Extract bullet points
            risk_items = re.findall(r'[-*]\s*(.+?)(?:\n|$)', risk_text)
            risks = [risk.strip() for risk in risk_items if risk.strip()]

        # Extract estimated time
        time_match = re.search(
            r'\*\*(?:Tempo )?Estimado?(?: Time)?[:\*]\*\*\s*(.+?)(?:\n|$)',
            ai_output,
            re.IGNORECASE
        )
        estimated_duration = time_match.group(1).strip() if time_match else None

        # Detect if requires root/admin
        requires_root = False
        if detected_language in ["bash", "shell", "sh"]:
            requires_root = bool(re.search(r'(sudo\s+|if.*EUID.*root|su\s+-)', script_content))
        elif detected_language == "powershell":
            requires_root = bool(re.search(r'(RunAsAdministrator|elevation required)', script_content, re.IGNORECASE))

        return {
            "script_content": script_content,
            "script_language": detected_language,
            "validation_command": validation_command,
            "estimated_duration": estimated_duration,
            "requires_root": requires_root,
            "risks": risks
        }
