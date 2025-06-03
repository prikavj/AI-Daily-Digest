"""
Search tool for verifying claims using Serper.dev API.
"""

import os
from typing import List, Dict, Optional
import requests
import logging
from dataclasses import dataclass
from datetime import datetime
import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

@dataclass
class SearchResult:
    """Data class to store search result information."""
    title: str
    url: str
    snippet: str
    source: str
    date: Optional[datetime] = None

class VerifyClaimToolSchema(BaseModel):
    """Schema for the verify claim tool input."""
    claim: str = Field(
        description="The claim to verify"
    )

class CheckVerificationToolSchema(BaseModel):
    """Schema for the check verification tool input."""
    claim: str = Field(
        description="The claim to check verification status"
    )

class VerifyClaimTool(BaseTool):
    """Tool for verifying claims using search."""
    
    name: str = "VerifyClaim"
    description: str = "Verify a specific claim by searching trusted sources"
    args_schema: type[BaseModel] = VerifyClaimToolSchema
    
    config: Dict = Field(default_factory=dict)
    serper_api_key: Optional[str] = Field(default=None)
    
    def __init__(self, config_path: str = "config.yaml", **data):
        """Initialize the search tool."""
        super().__init__(**data)
        self._load_config(config_path)
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable not set")

    def _load_config(self, config_path: str) -> None:
        """Load configuration from yaml file."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _run(self, claim: str) -> List[SearchResult]:
        """
        Search for verification of a specific claim.
        Returns a list of relevant search results that can verify the claim.
        """
        logging.info(f"Verifying claim: {claim}")
        num_sources = self.config['verification']['min_sources']
        
        try:
            response = requests.post(
                self.config['api']['serper']['endpoint'],
                headers={
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": claim,
                    "num": num_sources
                }
            )
            response.raise_for_status()
            
            search_data = response.json().get("organic", [])
            results = []
            
            for item in search_data:
                try:
                    # Check if the source domain is trusted
                    domain = self._extract_domain(item.get("link", ""))
                    if domain in self.config['verification']['trusted_domains']:
                        result = SearchResult(
                            title=item.get("title", ""),
                            url=item.get("link", ""),
                            snippet=item.get("snippet", ""),
                            source=domain,
                            date=self._parse_date(item.get("date"))
                        )
                        results.append(result)
                        
                except Exception as e:
                    logging.error(f"Error processing search result: {e}")
                    continue
            
            logging.info(f"Found {len(results)} verification sources")
            return results
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error performing verification search: {e}")
            raise

    def _extract_domain(self, url: str) -> str:
        """Extract the domain from a URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except Exception:
            return url

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string into datetime object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

class CheckVerificationTool(BaseTool):
    """Tool for checking if a claim has been verified."""
    
    name: str = "CheckVerification"
    description: str = "Check if a claim has been verified by the minimum required sources"
    args_schema: type[BaseModel] = CheckVerificationToolSchema
    
    verify_tool: VerifyClaimTool = Field(default_factory=lambda: VerifyClaimTool())
    
    def _run(self, claim: str) -> bool:
        """
        Check if a claim can be verified by trusted sources.
        Returns True if the minimum number of trusted sources verify the claim.
        """
        results = self.verify_tool._run(claim)
        min_sources = self.verify_tool.config['verification']['min_sources']
        return len(results) >= min_sources 