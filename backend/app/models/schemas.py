"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# Agent schemas
class Agent(BaseModel):
    """Wazuh agent information."""

    id: str
    name: str
    ip: Optional[str] = None
    status: Optional[str] = None
    os: Optional[dict] = None


# SCA Policy schemas
class SCAPolicy(BaseModel):
    """SCA policy information."""

    policy_id: str
    name: str
    description: Optional[str] = None
    references: Optional[str] = None


# SCA Check schemas
class SCACheck(BaseModel):
    """SCA check information."""

    id: int
    title: str
    description: Optional[str] = None
    rationale: Optional[str] = None
    remediation: Optional[str] = None
    compliance: Optional[List[dict]] = None
    rules: Optional[List[dict]] = None
    result: str  # passed, failed, not applicable


class SCACheckDetails(SCACheck):
    """Detailed SCA check information."""

    condition: Optional[str] = None
    file: Optional[str] = None
    directory: Optional[str] = None
    process: Optional[str] = None
    registry: Optional[str] = None
    command: Optional[str] = None
    reason: Optional[str] = None  # Specific reason why check failed


# Remediation Script schemas
class RemediationScript(BaseModel):
    """Executable remediation script."""

    script_content: str = Field(..., description="Complete script content")
    script_language: Literal["bash", "powershell", "python"] = Field(
        ..., description="Script language/shell"
    )
    validation_command: str = Field(..., description="Command to validate the fix")
    estimated_duration: Optional[str] = Field(
        None, description="Estimated execution time (e.g., '< 5 seconds')"
    )
    requires_root: bool = Field(
        default=False, description="Whether script requires root/admin privileges"
    )
    risks: List[str] = Field(
        default_factory=list, description="List of potential risks or warnings"
    )


# Analysis request/response schemas
class AnalysisRequest(BaseModel):
    """Request to analyze an SCA check."""

    agent_id: str = Field(..., description="Wazuh agent ID")
    policy_id: str = Field(..., description="SCA policy ID")
    check_id: int = Field(..., description="SCA check ID")
    language: Literal["pt", "en"] = Field(default="en", description="Report language")
    ai_provider: Literal["vllm", "openai"] = Field(
        default="vllm", description="AI provider to use"
    )


class AnalysisResponse(BaseModel):
    """Analysis result."""

    check_id: int
    report: str
    remediation_script: Optional[RemediationScript] = Field(
        None, description="Executable remediation script (if available)"
    )
    ai_provider: str
    language: str
    cached_from_agent: Optional[str] = Field(
        None, description="Agent name if this analysis was reused from cache (shared cache)"
    )


# PDF Generation schemas
class PDFRequest(BaseModel):
    """Request to generate a PDF report."""

    agent_name: str
    check_id: int
    report_text: str
    language: Literal["pt", "en"] = Field(default="en")


class PDFResponse(BaseModel):
    """PDF generation response."""

    filename: str
    download_url: str


# Batch analysis schemas
class BatchAnalysisRequest(BaseModel):
    """Request to analyze multiple checks."""

    agent_id: str
    policy_id: str
    check_ids: List[int]
    language: Literal["pt", "en"] = Field(default="en")
    ai_provider: Literal["vllm", "openai"] = Field(default="vllm")


class BatchAnalysisResponse(BaseModel):
    """Batch analysis results."""

    results: List[AnalysisResponse]
    total: int
    successful: int
    failed: int


# Error response schema
class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: Optional[str] = None


# Analysis History schemas
class AnalysisHistoryResponse(BaseModel):
    """Single analysis history record."""

    id: str
    agent_id: str
    agent_name: str
    policy_id: str
    check_id: int
    check_title: str
    check_description: Optional[str] = None
    analysis_date: datetime
    language: Literal["pt", "en"]
    ai_provider: Literal["vllm", "openai"]
    report_text: str
    remediation_script: Optional[RemediationScript] = None  # MISSING FIELD - CRITICAL!
    status: Literal["pending", "completed", "failed"]
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class AnalysisHistoryListResponse(BaseModel):
    """List of analysis history records."""

    analyses: List[AnalysisHistoryResponse]
    total: int
    limit: int
    offset: int


class CacheStatsResponse(BaseModel):
    """Cache statistics."""

    total_analyses: int
    completed: int
    failed: int
    cached_valid: int
    cache_enabled: bool
    cache_ttl_hours: int
