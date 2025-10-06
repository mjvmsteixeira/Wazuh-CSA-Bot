"""SCA-related API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.schemas import SCAPolicy, SCACheck, SCACheckDetails
from app.services.wazuh_client import wazuh_client
from app.utils.exceptions import WazuhAPIError, CheckNotFoundError

router = APIRouter(prefix="/sca", tags=["sca"])


@router.get("/{agent_id}/policies", response_model=List[SCAPolicy])
async def get_agent_policies(agent_id: str):
    """
    Get SCA policies for an agent.

    Args:
        agent_id: Wazuh agent ID

    Returns:
        List of SCA policies
    """
    try:
        policies = await wazuh_client.get_sca_policies(agent_id)
        return policies
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/checks/{policy_id}", response_model=List[SCACheck])
async def get_policy_checks(
    agent_id: str,
    policy_id: str,
    result: Optional[str] = Query(
        None, description="Filter by result (passed, failed, not applicable)"
    ),
    limit: int = Query(1000, description="Maximum number of checks to return"),
):
    """
    Get SCA checks for an agent and policy.

    Args:
        agent_id: Wazuh agent ID
        policy_id: SCA policy ID
        result: Optional filter by result status
        limit: Maximum number of results

    Returns:
        List of SCA checks
    """
    try:
        checks = await wazuh_client.get_sca_checks(
            agent_id, policy_id, result=result, limit=limit
        )
        return checks
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/checks/{policy_id}/failed", response_model=List[SCACheck])
async def get_failed_checks(agent_id: str, policy_id: str):
    """
    Get only failed SCA checks for an agent and policy.

    Args:
        agent_id: Wazuh agent ID
        policy_id: SCA policy ID

    Returns:
        List of failed SCA checks
    """
    try:
        checks = await wazuh_client.get_failed_checks(agent_id, policy_id)
        return checks
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{agent_id}/checks/{policy_id}/{check_id}", response_model=SCACheckDetails
)
async def get_check_details(agent_id: str, policy_id: str, check_id: int):
    """
    Get detailed information about a specific check.

    Args:
        agent_id: Wazuh agent ID
        policy_id: SCA policy ID
        check_id: SCA check ID

    Returns:
        Detailed check information
    """
    try:
        check = await wazuh_client.get_check_details(agent_id, policy_id, check_id)
        return check
    except CheckNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
