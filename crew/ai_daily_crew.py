"""
AI Daily Crew orchestration for coordinating the news digest generation process.
"""

from crewai import Crew, Task
from typing import List
from agents.harvester_agent import HarvesterAgent
from agents.summarizer_agent import SummarizerAgent
from agents.verifier_agent import VerifierAgent
from agents.editor_agent import EditorAgent
import logging

class AIDailyCrew:
    """Crew for orchestrating the AI news digest generation process."""
    
    def __init__(self):
        """Initialize the crew with all necessary agents."""
        self.logger = logging.getLogger(__name__)
        
        # Create all agents
        self.harvester = HarvesterAgent.create()
        self.summarizer = SummarizerAgent.create()
        self.verifier = VerifierAgent.create()
        self.editor = EditorAgent.create()
        
        # Create tasks
        self.tasks = [
            Task(
                description="""Gather today's most important AI news articles. Focus on significant 
                developments, breakthroughs, and major industry news. Ensure articles 
                are from reputable sources and are properly dated.""",
                expected_output="""A list of relevant AI news articles, each containing:
                - Title
                - URL
                - Source
                - Publication date
                - Brief snippet or description""",
                agent=self.harvester
            ),
            Task(
                description="""Analyze and summarize the gathered AI news articles. Create 
                comprehensive summaries that capture main points, maintain technical 
                accuracy, are clear and engaging, and identify key takeaways. Each 
                summary should be 1-2 paragraphs long.""",
                expected_output="""A list of article summaries, each containing:
                - Original article metadata (title, URL, source, date)
                - Comprehensive 1-2 paragraph summary
                - List of key takeaways or bullet points""",
                agent=self.summarizer
            ),
            Task(
                description="""Verify the claims made in the article summaries by 
                cross-referencing with trusted sources. Check technical accuracy,
                potential biases, and assess overall credibility. Provide verification 
                sources and confidence levels.""",
                expected_output="""A list of verified summaries, each containing:
                - Original summary content
                - Verification sources used
                - Verification status (verified/partially verified/unverified)
                - Confidence score
                - Any corrections or clarifications needed""",
                agent=self.verifier
            ),
            Task(
                description="""Compile the verified AI news summaries into a professional 
                digest. Format with a clear title and date, brief introduction, 
                main stories section, sources and verification status. Ensure proper 
                Markdown formatting and include all necessary attribution and links.""",
                expected_output="""A professionally formatted Markdown document containing:
                - Title and date
                - Brief introduction/overview
                - Main stories section with verified summaries
                - Sources and verification status
                - All necessary attribution and links""",
                agent=self.editor
            )
        ]
        
        # Create the crew
        self.crew = Crew(
            agents=[
                self.harvester,
                self.summarizer,
                self.verifier,
                self.editor
            ],
            tasks=self.tasks,
            verbose=True
        )

    def run(self) -> str:
        """
        Execute the full digest generation process.
        Returns the path to the generated digest file.
        """
        try:
            self.logger.info("Starting AI news digest generation...")
            result = self.crew.kickoff()
            self.logger.info("AI news digest generation completed successfully!")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating digest: {e}")
            raise 