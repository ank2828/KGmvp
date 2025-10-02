import httpx
from typing import Optional, Dict, Any
from app.config import settings


class PipedreamClient:
    """Client for interacting with Pipedream Connect API - Production Pattern"""

    def __init__(self):
        self.client_id = settings.PIPEDREAM_CLIENT_ID
        self.client_secret = settings.PIPEDREAM_CLIENT_SECRET
        self.project_id = settings.PIPEDREAM_PROJECT_ID
        self.project_environment = "production"  # or "development"
        self.base_url = "https://api.pipedream.com/v1"
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def create_connect_token(self, external_user_id: str = "user_main") -> Dict[str, str]:
        """
        Generate a Pipedream Connect token and URL for OAuth flow

        PROVEN PATTERN: Returns connectLinkUrl that's ready to use

        Args:
            external_user_id: Identifier for the user (email or stable ID)

        Returns:
            Dict with "token" and "connectLinkUrl"
        """
        response = await self.http_client.post(
            f"{self.base_url}/connect/tokens",
            json={
                "project_id": self.project_id,
                "external_user_id": external_user_id,
                "project_environment": self.project_environment
            },
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        data = response.json()

        # Return both token and ready-to-use URL
        return {
            "token": data["token"],
            "connectLinkUrl": data["connect_link_url"]  # Key addition!
        }

    async def list_accounts(self, external_user_id: str) -> list:
        """
        List all connected accounts for a user

        PROVEN PATTERN: Check what apps user has connected

        Args:
            external_user_id: User's ID

        Returns:
            List of account dicts with app info
        """
        response = await self.http_client.get(
            f"{self.base_url}/connect/accounts",
            params={"external_user_id": external_user_id},
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    async def get_account_for_app(self, external_user_id: str, app_name: str) -> Optional[str]:
        """
        Get account ID for specific app (gmail, hubspot, etc.)

        PROVEN PATTERN: Find the right account ID for SDK calls

        Args:
            external_user_id: User's ID
            app_name: App slug (gmail, hubspot, google_sheets, etc.)

        Returns:
            Account ID or None
        """
        accounts = await self.list_accounts(external_user_id)

        for account in accounts:
            if account.get("app", {}).get("name_slug") == app_name:
                return account.get("id")

        return None

    async def run_action(
        self,
        action_id: str,
        external_user_id: str,
        configured_props: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a Pipedream action (SDK pattern)

        PROVEN PATTERN: Execute actions like gmail-find-email

        Args:
            action_id: Action ID (e.g., "gmail-find-email")
            external_user_id: User's ID
            configured_props: Action props including auth

        Returns:
            Action result
        """
        response = await self.http_client.post(
            f"{self.base_url}/actions/run",
            json={
                "id": action_id,
                "external_user_id": external_user_id,
                "configured_props": configured_props
            },
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        result = response.json()

        # Check for errors (proven pattern)
        if result.get("os") and isinstance(result["os"], list):
            error_item = next((item for item in result["os"] if item.get("k") == "error"), None)
            if error_item and error_item.get("err"):
                raise Exception(error_item["err"].get("message", "Action failed"))

        return result.get("ret") or result.get("data") or result

    async def deploy_trigger(
        self,
        trigger_id: str,
        external_user_id: str,
        webhook_url: str,
        configured_props: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy a monitoring trigger

        PROVEN PATTERN: Set up continuous email monitoring

        Args:
            trigger_id: Trigger ID (e.g., "gmail-new-email")
            external_user_id: User's ID
            webhook_url: Where to send events
            configured_props: Trigger configuration

        Returns:
            Trigger deployment info
        """
        response = await self.http_client.post(
            f"{self.base_url}/triggers/deploy",
            json={
                "id": trigger_id,
                "external_user_id": external_user_id,
                "webhook_url": webhook_url,
                "configured_props": configured_props
            },
            auth=(self.client_id, self.client_secret)
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()


# Global instance
pipedream_client = PipedreamClient()
