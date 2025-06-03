"""
HarvesterAgent for gathering AI-related news articles.
"""

from typing import List
from crewai import Agent
from tools.news_scraper_tool import NewsScraperTool, NewsArticle

class HarvesterAgent:
    """Agent responsible for gathering AI-related news articles."""
    
    @staticmethod
    def create() -> Agent:
        """Create and return the HarvesterAgent."""
        return Agent(
            role='News Harvester',
            goal='Gather the most relevant and recent AI news articles',
            backstory="""You are an expert news curator with a deep understanding 
            of artificial intelligence and technology. Your task is to gather the 
            most significant AI news stories of the day.""",
            tools=[NewsScraperTool()],
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    async def execute(agent: Agent) -> List[NewsArticle]:
        """
        Execute the harvesting task.
        Returns a list of gathered news articles.
        """
        task_result = await agent.execute(
            "Gather today's most important AI news articles. Focus on significant "
            "developments, breakthroughs, and major industry news. Ensure articles "
            "are from reputable sources and are properly dated."
        )
        
        # The agent's tool will return a List[NewsArticle]
        return task_result 