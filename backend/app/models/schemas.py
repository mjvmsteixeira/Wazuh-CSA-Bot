"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal


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
    ai_provider: str
    language: str


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
