"""SQLAlchemy ORM models for database tables."""

import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import event

from app.db.base import Base


def generate_uuid():
    """Generate UUID as string for SQLite compatibility."""
    return str(uuid.uuid4())


class AnalysisHistory(Base):
    """
    Model for storing SCA analysis history.

    This table serves as:
    1. Cache for expensive AI analysis calls
    2. Historical record for compliance tracking
    3. Audit trail for analysis changes over time
    """

    __tablename__ = "analysis_history"

    # Primary Key
    id = Column(String(36), primary_key=True, default=generate_uuid)

    # Identifiers (indexed for fast lookups)
    agent_id = Column(String(50), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    policy_id = Column(String(100), nullable=False)
    check_id = Column(Integer, nullable=False, index=True)

    # Check Information (for display/search)
    check_title = Column(String(500), nullable=False)
    check_description = Column(Text, nullable=True)

    # Analysis Metadata
    analysis_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    language = Column(String(2), nullable=False)  # 'pt' or 'en'
    ai_provider = Column(String(20), nullable=False)  # 'vllm' or 'openai'

    # Analysis Content
    report_text = Column(Text, nullable=False)

    # Remediation Script (NEW)
    remediation_script = Column(Text, nullable=True)  # Script content
    script_language = Column(String(20), nullable=True)  # bash, powershell, python
    validation_command = Column(Text, nullable=True)  # Command to validate fix
    script_metadata = Column(Text, nullable=True)  # JSON: {estimated_duration, requires_root, risks[]}

    # Status and Performance
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, nullable=True)

    # Composite Indexes for optimized queries
    __table_args__ = (
        Index('idx_agent_check', 'agent_id', 'check_id'),
        Index('idx_date_status', 'analysis_date', 'status'),
        Index('idx_policy_check', 'policy_id', 'check_id'),
    )

    def __repr__(self):
        return (
            f"<AnalysisHistory(id={self.id}, agent={self.agent_name}, "
            f"check={self.check_id}, date={self.analysis_date}, status={self.status})>"
        )

    def to_dict(self):
        """Convert model to dictionary for API responses."""
        result = {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "policy_id": self.policy_id,
            "check_id": self.check_id,
            "check_title": self.check_title,
            "check_description": self.check_description,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "language": self.language,
            "ai_provider": self.ai_provider,
            "report_text": self.report_text,
            "status": self.status,
            "error_message": self.error_message,
            "execution_time_seconds": self.execution_time_seconds,
        }

        # Add remediation script if available
        if self.remediation_script:
            metadata = {}
            if self.script_metadata:
                try:
                    metadata = json.loads(self.script_metadata)
                except (json.JSONDecodeError, TypeError):
                    pass

            result["remediation_script"] = {
                "script_content": self.remediation_script,
                "script_language": self.script_language,
                "validation_command": self.validation_command,
                **metadata
            }

        return result
