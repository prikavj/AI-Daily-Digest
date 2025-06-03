"""
VerifierAgent for fact-checking article claims.
"""

from typing import List, Dict
from crewai import Agent
from tools.search_tool import VerifyClaimTool, CheckVerificationTool
from agents.summarizer_agent import ArticleSummary
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VerifiedSummary(ArticleSummary):
    """Data class to store verified article summary information."""
    verification_sources: List[Dict[str, str]]
    verification_status: str
    confidence_score: float

class VerifierAgent:
    """Agent responsible for verifying article claims."""
    
    @staticmethod
    def create() -> Agent:
        """Create and return the VerifierAgent."""
        return Agent(
            role='Fact Checker',
            goal='Verify the accuracy of AI news article claims',
            backstory="""You are a meticulous fact-checker with expertise in AI 
            and technology. Your role is to verify claims made in news articles 
            by cross-referencing them with trusted sources.""",
            tools=[VerifyClaimTool(), CheckVerificationTool()],
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    async def execute(
        agent: Agent, 
        summaries: List[ArticleSummary]
    ) -> List[VerifiedSummary]:
        """
        Execute the verification task.
        Returns a list of verified article summaries.
        """
        verified_summaries = []
        
        for summary in summaries:
            task_result = await agent.execute(
                f"""Verify the following AI news article summary:
                Title: {summary.title}
                Summary: {summary.summary}
                Key Points: {', '.join(summary.key_points)}
                
                For each main claim:
                1. Cross-reference with trusted sources
                2. Verify technical accuracy
                3. Check for potential biases
                4. Assess overall credibility
                
                Provide verification sources and confidence level.
                """
            )
            
            # Parse the agent's response into a VerifiedSummary
            verified = VerifiedSummary(
                title=summary.title,
                url=summary.url,
                source=summary.source,
                published_date=summary.published_date,
                summary=summary.summary,
                key_points=summary.key_points,
                verification_sources=task_result.get('sources', []),
                verification_status=task_result.get('status', 'unverified'),
                confidence_score=float(task_result.get('confidence', 0.0))
            )
            
            verified_summaries.append(verified)
        
        return verified_summaries 