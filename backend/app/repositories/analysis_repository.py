"""Repository for analysis history database operations."""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
import json

from app.db.models import AnalysisHistory
from app.config import settings
from app.utils.logger import logger


class AnalysisRepository:
    """Repository for CRUD operations on analysis history."""

    def __init__(self, db: Session):
        self.db = db

    def save_analysis(
        self,
        agent_id: str,
        agent_name: str,
        policy_id: str,
        check_id: int,
        check_title: str,
        language: str,
        ai_provider: str,
        report_text: str,
        status: str = "completed",
        error_message: Optional[str] = None,
        execution_time: Optional[float] = None,
        check_description: Optional[str] = None,
        remediation_script: Optional[Dict[str, Any]] = None,
    ) -> AnalysisHistory:
        """
        Save a new analysis to history.

        Args:
            agent_id: Wazuh agent ID
            agent_name: Wazuh agent name
            policy_id: SCA policy ID
            check_id: SCA check ID
            check_title: Check title for display
            language: Report language ('pt' or 'en')
            ai_provider: AI provider used ('vllm' or 'openai')
            report_text: Generated analysis report
            status: Analysis status (default: 'completed')
            error_message: Error message if failed
            execution_time: Time taken in seconds
            check_description: Optional check description
            remediation_script: Optional dict with script data

        Returns:
            Created AnalysisHistory instance
        """
        # Extract script fields if provided
        script_content = None
        script_language = None
        validation_command = None
        script_metadata_json = None

        if remediation_script:
            script_content = remediation_script.get("script_content")
            script_language = remediation_script.get("script_language")
            validation_command = remediation_script.get("validation_command")

            # Store metadata as JSON
            metadata = {
                "estimated_duration": remediation_script.get("estimated_duration"),
                "requires_root": remediation_script.get("requires_root", False),
                "risks": remediation_script.get("risks", []),
            }
            script_metadata_json = json.dumps(metadata)

        analysis = AnalysisHistory(
            agent_id=agent_id,
            agent_name=agent_name,
            policy_id=policy_id,
            check_id=check_id,
            check_title=check_title,
            check_description=check_description,
            language=language,
            ai_provider=ai_provider,
            report_text=report_text,
            status=status,
            error_message=error_message,
            execution_time_seconds=execution_time,
            remediation_script=script_content,
            script_language=script_language,
            validation_command=validation_command,
            script_metadata=script_metadata_json,
        )

        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)

        logger.info(
            f"Saved analysis to history: agent={agent_name}, "
            f"check={check_id}, provider={ai_provider}, status={status}"
            + (f", script={script_language}" if script_content else "")
        )

        return analysis

    def find_cached_analysis(
        self,
        agent_id: str,
        check_id: int,
        language: str,
        max_age_hours: Optional[int] = None,
    ) -> Optional[AnalysisHistory]:
        """
        Find a recent cached analysis for the given parameters.

        Args:
            agent_id: Wazuh agent ID
            check_id: SCA check ID
            language: Report language
            max_age_hours: Maximum age in hours (default from settings)

        Returns:
            Most recent matching analysis if found and valid, None otherwise
        """
        if not settings.enable_analysis_cache:
            return None

        max_age = max_age_hours or settings.analysis_cache_ttl_hours
        cutoff_date = datetime.utcnow() - timedelta(hours=max_age)

        analysis = (
            self.db.query(AnalysisHistory)
            .filter(
                and_(
                    AnalysisHistory.agent_id == agent_id,
                    AnalysisHistory.check_id == check_id,
                    AnalysisHistory.language == language,
                    AnalysisHistory.status == "completed",
                    AnalysisHistory.analysis_date >= cutoff_date,
                )
            )
            .order_by(desc(AnalysisHistory.analysis_date))
            .first()
        )

        if analysis:
            logger.info(
                f"Cache HIT (agent-specific): agent={agent_id}, check={check_id}, "
                f"age={datetime.utcnow() - analysis.analysis_date}"
            )
        else:
            logger.info(f"Cache MISS (agent-specific): agent={agent_id}, check={check_id}")

        return analysis

    def find_cached_analysis_by_check_id(
        self,
        check_id: int,
        language: str,
        exclude_agent_id: Optional[str] = None,
        max_age_hours: Optional[int] = None,
    ) -> Optional[AnalysisHistory]:
        """
        Find a recent cached analysis for ANY agent with the same check_id.
        This allows reusing analyses across different agents for the same check.

        Args:
            check_id: Check ID to search for
            language: Report language
            exclude_agent_id: Optional agent ID to exclude (to avoid returning same agent's cache)
            max_age_hours: Maximum age in hours (default from settings)

        Returns:
            Most recent matching analysis if found and valid, None otherwise
        """
        if not settings.enable_analysis_cache:
            return None

        max_age = max_age_hours or settings.analysis_cache_ttl_hours
        cutoff_date = datetime.utcnow() - timedelta(hours=max_age)

        query = self.db.query(AnalysisHistory).filter(
            and_(
                AnalysisHistory.check_id == check_id,
                AnalysisHistory.language == language,
                AnalysisHistory.status == "completed",
                AnalysisHistory.analysis_date >= cutoff_date,
            )
        )

        # Exclude the requesting agent's own cache (to force shared cache)
        if exclude_agent_id:
            query = query.filter(AnalysisHistory.agent_id != exclude_agent_id)

        analysis = query.order_by(desc(AnalysisHistory.analysis_date)).first()

        if analysis:
            logger.info(
                f"Cache HIT (shared): check_id={check_id}, "
                f"original_agent={analysis.agent_name}, "
                f"age={datetime.utcnow() - analysis.analysis_date}"
            )
        else:
            logger.info(f"Cache MISS (shared): check_id={check_id}")

        return analysis

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisHistory]:
        """Get analysis by ID."""
        return (
            self.db.query(AnalysisHistory)
            .filter(AnalysisHistory.id == analysis_id)
            .first()
        )

    def get_history_by_agent(
        self,
        agent_id: str,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> List[AnalysisHistory]:
        """
        Get analysis history for a specific agent.

        Args:
            agent_id: Wazuh agent ID
            limit: Maximum number of results
            offset: Pagination offset
            status_filter: Optional status filter

        Returns:
            List of analysis history records
        """
        query = self.db.query(AnalysisHistory).filter(
            AnalysisHistory.agent_id == agent_id
        )

        if status_filter:
            query = query.filter(AnalysisHistory.status == status_filter)

        return (
            query.order_by(desc(AnalysisHistory.analysis_date))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_history_by_check(
        self,
        agent_id: str,
        check_id: int,
        limit: int = 20,
    ) -> List[AnalysisHistory]:
        """
        Get analysis history for a specific check.

        Args:
            agent_id: Wazuh agent ID
            check_id: SCA check ID
            limit: Maximum number of results

        Returns:
            List of analysis history records for the check
        """
        return (
            self.db.query(AnalysisHistory)
            .filter(
                and_(
                    AnalysisHistory.agent_id == agent_id,
                    AnalysisHistory.check_id == check_id,
                )
            )
            .order_by(desc(AnalysisHistory.analysis_date))
            .limit(limit)
            .all()
        )

    def get_recent_analyses(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> List[AnalysisHistory]:
        """
        Get recent analyses across all agents.

        Args:
            hours: Look back window in hours
            limit: Maximum number of results

        Returns:
            List of recent analysis records
        """
        cutoff_date = datetime.utcnow() - timedelta(hours=hours)

        return (
            self.db.query(AnalysisHistory)
            .filter(AnalysisHistory.analysis_date >= cutoff_date)
            .order_by(desc(AnalysisHistory.analysis_date))
            .limit(limit)
            .all()
        )

    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis from history.

        Args:
            analysis_id: Analysis ID to delete

        Returns:
            True if deleted, False if not found
        """
        analysis = self.get_by_id(analysis_id)
        if analysis:
            self.db.delete(analysis)
            self.db.commit()
            logger.info(f"Deleted analysis from history: id={analysis_id}")
            return True
        return False

    def count_by_agent(self, agent_id: str) -> int:
        """Count total analyses for an agent."""
        return (
            self.db.query(AnalysisHistory)
            .filter(AnalysisHistory.agent_id == agent_id)
            .count()
        )

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        total = self.db.query(AnalysisHistory).count()
        completed = (
            self.db.query(AnalysisHistory)
            .filter(AnalysisHistory.status == "completed")
            .count()
        )
        failed = (
            self.db.query(AnalysisHistory)
            .filter(AnalysisHistory.status == "failed")
            .count()
        )

        cutoff = datetime.utcnow() - timedelta(hours=settings.analysis_cache_ttl_hours)
        cached = (
            self.db.query(AnalysisHistory)
            .filter(
                and_(
                    AnalysisHistory.status == "completed",
                    AnalysisHistory.analysis_date >= cutoff,
                )
            )
            .count()
        )

        return {
            "total_analyses": total,
            "completed": completed,
            "failed": failed,
            "cached_valid": cached,
            "cache_enabled": settings.enable_analysis_cache,
            "cache_ttl_hours": settings.analysis_cache_ttl_hours,
        }
