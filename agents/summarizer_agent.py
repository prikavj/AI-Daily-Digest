"""
SummarizerAgent for creating concise summaries of news articles.
"""

from typing import List, Dict
from crewai import Agent
from tools.news_scraper_tool import NewsArticle
from dataclasses import dataclass
from datetime import datetime
from crewai.tools import BaseTool

@dataclass
class ArticleSummary:
    """Data class to store article summary information."""
    title: str
    url: str
    source: str
    published_date: datetime
    summary: str
    key_points: List[str]

class SummarizeTool(BaseTool):
    """Tool for summarizing articles."""
    
    name: str = "SummarizeArticle"
    description: str = "Create a clear and concise summary of an article with key points"
    
    def _run(self, article_text: str) -> Dict[str, str]:
        """This tool uses the agent's LLM capabilities."""
        return {"summary": article_text}

class SummarizerAgent:
    """Agent responsible for creating concise article summaries."""
    
    @staticmethod
    def create() -> Agent:
        """Create and return the SummarizerAgent."""
        return Agent(
            role='Content Summarizer',
            goal='Create clear, accurate, and concise summaries of AI news articles',
            backstory="""You are an expert content analyst with a talent for 
            distilling complex technical information into clear, readable summaries. 
            You understand AI technology deeply and can explain it to others effectively.""",
            tools=[SummarizeTool()],
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    async def execute(agent: Agent, articles: List[NewsArticle]) -> List[ArticleSummary]:
        """
        Execute the summarization task.
        Returns a list of article summaries.
        """
        summaries = []
        
        for article in articles:
            task_result = await agent.execute(
                f"""Analyze and summarize the following AI news article:
                Title: {article.title}
                Content: {article.content or article.snippet}
                
                Create a comprehensive summary that:
                1. Captures the main points and significance
                2. Maintains technical accuracy
                3. Is clear and engaging
                4. Identifies key takeaways
                5. Is 1-2 paragraphs long
                
                Format the summary in a structured way with clear sections.
                """
            )
            
            # Parse the agent's response into an ArticleSummary
            summary = ArticleSummary(
                title=article.title,
                url=article.url,
                source=article.source,
                published_date=article.published_date,
                summary=task_result.get('summary', ''),
                key_points=task_result.get('key_points', [])
            )
            
            summaries.append(summary)
        
        return summaries 