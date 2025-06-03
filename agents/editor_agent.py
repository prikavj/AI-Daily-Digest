"""
EditorAgent for compiling and formatting the final AI news digest.
"""

from typing import List, Dict
from crewai import Agent
from agents.verifier_agent import VerifiedSummary
from datetime import datetime
import yaml
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

class FormatDigestSchema(BaseModel):
    """Schema for the format digest tool input."""
    content: str = Field(
        description="The content to format into a digest"
    )
    title: str = Field(
        default="AI News Digest",
        description="The title of the digest"
    )

class FormatDigestTool(BaseTool):
    """Tool for formatting the final digest."""
    
    name: str = "FormatDigest"
    description: str = "Format and compile verified news summaries into a professional digest"
    args_schema: type[BaseModel] = FormatDigestSchema
    _config: Dict = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from config.yaml."""
        with open("config.yaml", 'r') as f:
            return yaml.safe_load(f)

    def _run(self, content: str, title: str = "AI News Digest") -> str:
        """Format and save the digest."""
        try:
            # Create digests directory if it doesn't exist
            os.makedirs("digests", exist_ok=True)
            
            # Save the digest with today's date
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"digests/ai_digest_{today}.md"
            
            with open(filename, "w") as f:
                f.write(content)
            
            return content
        except Exception as e:
            return f"Error saving digest: {str(e)}"

class EditorAgent:
    """Agent responsible for compiling and formatting the final digest."""
    
    @staticmethod
    def create() -> Agent:
        """Create and return the EditorAgent."""
        return Agent(
            role='Content Editor',
            goal='Create a well-organized, professional AI news digest',
            backstory="""You are a skilled editor with expertise in technology 
            journalism. Your role is to compile verified AI news summaries into 
            a cohesive, well-structured digest that provides value to readers.""",
            tools=[FormatDigestTool()],
            verbose=True,
            allow_delegation=False
        )

    @staticmethod
    async def execute(agent: Agent, verified_summaries: List[VerifiedSummary]) -> str:
        """
        Execute the digest compilation task.
        Returns the formatted digest as a string.
        """
        task_result = await agent.execute(
            f"""Compile the following verified AI news summaries into a professional digest:
            
            Summaries: {verified_summaries}
            
            Format the digest with:
            1. Brief introduction/overview
            2. Main stories section with verified summaries
            3. Sources and verification status
            4. Professional formatting in Markdown
            
            Ensure the digest is:
            - Well-organized and easy to read
            - Professional in tone
            - Properly formatted with Markdown
            - Includes all necessary attribution and links
            """
        )
        
        return task_result 