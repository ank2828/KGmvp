from openai import AsyncOpenAI
from typing import Dict, List
from app.config import settings
from app.services.graphiti_service import graphiti_service


class AgentService:
    """AI agent service for querying the knowledge graph and generating responses"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(self, message: str) -> Dict[str, any]:
        """
        Process a chat message and return AI response with sources

        Args:
            message: User's question or query

        Returns:
            Dict with "answer" and "sources" keys
        """
        # Search knowledge graph for relevant context
        search_results = await graphiti_service.search(query=message, num_results=10)

        # Extract facts from search results
        context_facts = []
        for edge in search_results[:5]:
            if hasattr(edge, 'fact'):
                context_facts.append(edge.fact)

        # Build context string
        context = "\n".join([f"- {fact}" for fact in context_facts]) if context_facts else "No relevant context found."

        # Create system prompt with context
        system_prompt = f"""You are a business intelligence assistant with access to Gmail and HubSpot data.

Relevant context from the knowledge graph:
{context}

Answer the user's question based on this context. Be concise, helpful, and cite specific information from the context when possible. If the context doesn't contain relevant information, let the user know."""

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": context_facts[:3]  # Return top 3 sources
        }


# Global instance
agent_service = AgentService()
