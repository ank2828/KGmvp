import httpx
from typing import Optional, Dict, Any
from app.config import settings


class PipedreamClient:
    """Client for interacting with Pipedream Connect API"""

    def __init__(self):
        self.client_id = settings.PIPEDREAM_CLIENT_ID
        self.client_secret = settings.PIPEDREAM_CLIENT_SECRET
        self.project_id = settings.PIPEDREAM_PROJECT_ID
        self.base_url = "https://api.pipedream.com/v1"
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def create_connect_token(self, external_user_id: str = "user_main") -> str:
        """
        Generate a Pipedream Connect token for OAuth flow

        Args:
            external_user_id: Identifier for the user (default: "user_main" for MVP)

        Returns:
            Connect token string
        """
        response = await self.http_client.post(
            f"{self.base_url}/connect/tokens",
            json={
                "project_id": self.project_id,
                "external_user_id": external_user_id
            },
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        return response.json()["token"]

    async def proxy_request(
        self,
        account_id: str,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request via Pipedream proxy on behalf of a connected account

        Args:
            account_id: Pipedream account ID (e.g., "acc_abc123")
            method: HTTP method (GET, POST, etc.)
            url: Full API URL to call
            params: Query parameters
            json: JSON body for POST requests

        Returns:
            API response as dict
        """
        payload = {"method": method, "url": url}

        if params:
            payload["params"] = params
        if json:
            payload["json"] = json

        response = await self.http_client.post(
            f"{self.base_url}/connect/accounts/{account_id}/proxy",
            json=payload,
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()


# Global instance
pipedream_client = PipedreamClient()
