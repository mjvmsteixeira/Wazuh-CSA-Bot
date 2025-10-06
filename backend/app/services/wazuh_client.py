"""Wazuh API client service."""

import httpx
from typing import List, Dict, Any, Optional

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import WazuhAPIError, AgentNotFoundError, CheckNotFoundError


class WazuhClient:
    """Client for interacting with Wazuh API."""

    def __init__(self):
        self.api_url = settings.wazuh_api_url
        self.user = settings.wazuh_user
        self.password = settings.wazuh_password
        self.verify_ssl = settings.wazuh_verify_ssl
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        """Authenticate and get access token."""
        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/security/user/authenticate",
                    auth=(self.user, self.password),
                )
                response.raise_for_status()
                token = response.json()["data"]["token"]
                logger.info("Successfully authenticated with Wazuh API")
                return token
        except Exception as e:
            logger.error(f"Wazuh authentication failed: {e}")
            raise WazuhAPIError(f"Authentication failed: {str(e)}")

    async def _ensure_token(self) -> str:
        """Ensure we have a valid token."""
        if not self._token:
            self._token = await self._get_token()
        return self._token

    async def get_agents(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of agents, optionally filtered by search term."""
        token = await self._ensure_token()
        params = {}
        if search:
            params["search"] = search

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/agents",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
                response.raise_for_status()
                agents = response.json()["data"]["affected_items"]
                logger.info(f"Retrieved {len(agents)} agents")
                return agents
        except Exception as e:
            logger.error(f"Failed to get agents: {e}")
            raise WazuhAPIError(f"Failed to retrieve agents: {str(e)}")

    async def get_agent_by_name(self, agent_name: str) -> Dict[str, Any]:
        """Get specific agent by name."""
        agents = await self.get_agents(search=agent_name)
        if not agents:
            raise AgentNotFoundError(f"Agent '{agent_name}' not found")
        return agents[0]

    async def get_sca_policies(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get SCA policies for an agent."""
        token = await self._ensure_token()

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/sca/{agent_id}",
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
                policies = response.json()["data"]["affected_items"]
                logger.info(f"Retrieved {len(policies)} SCA policies for agent {agent_id}")
                return policies
        except Exception as e:
            logger.error(f"Failed to get SCA policies: {e}")
            raise WazuhAPIError(f"Failed to retrieve SCA policies: {str(e)}")

    async def get_sca_checks(
        self,
        agent_id: str,
        policy_id: str,
        result: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get SCA checks for an agent and policy."""
        token = await self._ensure_token()
        params = {"limit": limit}
        if result:
            params["result"] = result

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/sca/{agent_id}/checks/{policy_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
                response.raise_for_status()
                checks = response.json()["data"]["affected_items"]
                logger.info(
                    f"Retrieved {len(checks)} SCA checks for agent {agent_id}, policy {policy_id}"
                )
                return checks
        except Exception as e:
            logger.error(f"Failed to get SCA checks: {e}")
            raise WazuhAPIError(f"Failed to retrieve SCA checks: {str(e)}")

    async def get_failed_checks(
        self, agent_id: str, policy_id: str
    ) -> List[Dict[str, Any]]:
        """Get only failed SCA checks."""
        return await self.get_sca_checks(agent_id, policy_id, result="failed")

    async def get_check_details(
        self, agent_id: str, policy_id: str, check_id: int
    ) -> Dict[str, Any]:
        """Get details of a specific check."""
        token = await self._ensure_token()
        params = {"q": f"id~{check_id}"}

        try:
            async with httpx.AsyncClient(verify=self.verify_ssl) as client:
                response = await client.get(
                    f"{self.api_url}/sca/{agent_id}/checks/{policy_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                )
                response.raise_for_status()
                checks = response.json()["data"]["affected_items"]
                if not checks:
                    raise CheckNotFoundError(
                        f"Check {check_id} not found for agent {agent_id}"
                    )
                logger.info(f"Retrieved details for check {check_id}")
                return checks[0]
        except CheckNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get check details: {e}")
            raise WazuhAPIError(f"Failed to retrieve check details: {str(e)}")


# Singleton instance
wazuh_client = WazuhClient()
