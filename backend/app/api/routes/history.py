"""Analysis history API endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import Optional

from app.models.schemas import (
    AnalysisHistoryResponse,
    AnalysisHistoryListResponse,
    CacheStatsResponse,
)
from app.db.session import get_db
from app.repositories.analysis_repository import AnalysisRepository
from app.utils.logger import logger

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/agent/{agent_id}", response_model=AnalysisHistoryListResponse)
async def get_agent_history(
    agent_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(pending|completed|failed)$"),
    db: Session = Depends(get_db),
):
    """
    Get analysis history for a specific agent.

    Args:
        agent_id: Wazuh agent ID
        limit: Maximum number of results (1-200)
        offset: Pagination offset
        status: Optional status filter
        db: Database session

    Returns:
        List of analysis history records
    """
    repo = AnalysisRepository(db)

    try:
        analyses = repo.get_history_by_agent(
            agent_id=agent_id,
            limit=limit,
            offset=offset,
            status_filter=status,
        )

        total = repo.count_by_agent(agent_id)

        return AnalysisHistoryListResponse(
            analyses=[AnalysisHistoryResponse.model_validate(a) for a in analyses],
            total=total,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(f"Failed to get agent history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{agent_id}/{check_id}", response_model=AnalysisHistoryListResponse)
async def get_check_history(
    agent_id: str,
    check_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get analysis history for a specific check.

    Args:
        agent_id: Wazuh agent ID
        check_id: SCA check ID
        limit: Maximum number of results
        db: Database session

    Returns:
        List of analysis history records for the check
    """
    repo = AnalysisRepository(db)

    try:
        analyses = repo.get_history_by_check(
            agent_id=agent_id,
            check_id=check_id,
            limit=limit,
        )

        return AnalysisHistoryListResponse(
            analyses=[AnalysisHistoryResponse(**a.to_dict()) for a in analyses],
            total=len(analyses),
            limit=limit,
            offset=0,
        )

    except Exception as e:
        logger.error(f"Failed to get check history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}", response_model=AnalysisHistoryResponse)
async def get_analysis_by_id(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific analysis by ID.

    Args:
        analysis_id: Analysis history ID
        db: Database session

    Returns:
        Analysis history record
    """
    repo = AnalysisRepository(db)

    try:
        analysis = repo.get_by_id(analysis_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return AnalysisHistoryResponse(**analysis.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete an analysis from history.

    Args:
        analysis_id: Analysis history ID
        db: Database session

    Returns:
        Success message
    """
    repo = AnalysisRepository(db)

    try:
        deleted = repo.delete_analysis(analysis_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return {"message": "Analysis deleted successfully", "id": analysis_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/cache", response_model=CacheStatsResponse)
async def get_cache_stats(db: Session = Depends(get_db)):
    """
    Get cache statistics.

    Args:
        db: Database session

    Returns:
        Cache statistics including hit rates and totals
    """
    repo = AnalysisRepository(db)

    try:
        stats = repo.get_cache_stats()
        return CacheStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=AnalysisHistoryListResponse)
async def get_recent_analyses(
    hours: int = Query(24, ge=1, le=168),  # Max 1 week
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Get recent analyses across all agents.

    Args:
        hours: Look back window in hours (1-168, default 24)
        limit: Maximum number of results (default 100)
        db: Database session

    Returns:
        List of recent analysis records
    """
    repo = AnalysisRepository(db)

    try:
        analyses = repo.get_recent_analyses(hours=hours, limit=limit)

        return AnalysisHistoryListResponse(
            analyses=[AnalysisHistoryResponse(**a.to_dict()) for a in analyses],
            total=len(analyses),
            limit=limit,
            offset=0,
        )

    except Exception as e:
        logger.error(f"Failed to get recent analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))
