from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from app.config import settings
from typing import List, Any


class GraphitiService:
    """Service for managing Graphiti knowledge graph operations"""

    def __init__(self):
        driver_params = {
            "host": settings.FALKORDB_HOST,
            "port": settings.FALKORDB_PORT,
            "database": settings.FALKORDB_DATABASE
        }

        # Add auth if credentials are provided
        if settings.FALKORDB_USERNAME:
            driver_params["username"] = settings.FALKORDB_USERNAME
        if settings.FALKORDB_PASSWORD:
            driver_params["password"] = settings.FALKORDB_PASSWORD

        self.driver = FalkorDriver(**driver_params)
        self.graphiti = Graphiti(graph_driver=self.driver)
        self._initialized = False

    async def initialize(self):
        """Initialize Graphiti indices and constraints (call on startup)"""
        if not self._initialized:
            await self.graphiti.build_indices_and_constraints()
            self._initialized = True

    async def add_episode(
        self,
        content: str,
        source: str,
        name: str = None,
        reference_time: Any = None,
        uuid: str = None,
        **kwargs
    ) -> Any:
        """
        Add an episode to the knowledge graph

        Args:
            content: Text content of the episode (email body, contact info, etc.)
            source: Description of the data source
            name: Optional name for the episode
            reference_time: Timestamp for temporal tracking
            uuid: Unique identifier to prevent duplicates
            **kwargs: Additional metadata

        Returns:
            Episode result from Graphiti
        """
        return await self.graphiti.add_episode(
            episode_body=content,
            source_description=source,
            group_id="user_main",  # Single user for MVP
            name=name,
            reference_time=reference_time,
            uuid=uuid,
            **kwargs
        )

    async def search(self, query: str, num_results: int = 10) -> List[Any]:
        """
        Search the knowledge graph

        Args:
            query: Search query string
            num_results: Maximum number of results to return

        Returns:
            List of search results (edges with facts)
        """
        return await self.graphiti.search(
            query=query,
            group_ids=["user_main"],
            num_results=num_results
        )

    async def close(self):
        """Close the graph driver connection"""
        await self.driver.close()


# Global instance
graphiti_service = GraphitiService()
