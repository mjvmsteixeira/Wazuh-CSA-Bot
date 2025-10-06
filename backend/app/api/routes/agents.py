"""Agent-related API endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.models.schemas import Agent, ErrorResponse
from app.services.wazuh_client import wazuh_client
from app.utils.exceptions import WazuhAPIError, AgentNotFoundError

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=List[Agent])
async def list_agents(
    search: Optional[str] = Query(None, description="Search term for agent name"),
):
    """
    Get list of Wazuh agents.

    Args:
        search: Optional search term to filter agents by name

    Returns:
        List of agents
    """
    try:
        agents = await wazuh_client.get_agents(search=search)
        return agents
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """
    Get specific agent by ID.

    Args:
        agent_id: Wazuh agent ID

    Returns:
        Agent information
    """
    try:
        agents = await wazuh_client.get_agents()
        agent = next((a for a in agents if a["id"] == agent_id), None)
        if not agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        return agent
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/name/{agent_name}", response_model=Agent)
async def get_agent_by_name(agent_name: str):
    """
    Get agent by name.

    Args:
        agent_name: Agent name

    Returns:
        Agent information
    """
    try:
        agent = await wazuh_client.get_agent_by_name(agent_name)
        return agent
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except WazuhAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
