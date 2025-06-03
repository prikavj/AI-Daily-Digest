"""
News scraper tool for fetching AI-related news articles using Serper.dev API.
"""

import os
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional, ClassVar
from dataclasses import dataclass
import yaml
import logging
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from urllib.parse import urlparse
import json

@dataclass
class NewsArticle:
    """Data class to store news article information."""
    title: str
    url: str
    source: str
    published_date: datetime
    snippet: str
    content: Optional[str] = None

class NewsScraperToolSchema(BaseModel):
    """Schema for the news scraper tool input."""
    query: str = Field(
        default="artificial intelligence news",
        description="The search query for fetching news articles"
    )

class NewsScraperTool(BaseTool):
    """Tool for fetching AI-related news articles."""
    
    name: str = "FetchNewsArticles"
    description: str = "Fetch recent AI news articles from trusted sources"
    args_schema: type[BaseModel] = NewsScraperToolSchema
    logger: ClassVar[logging.Logger] = logging.getLogger(__name__)
    _config: Dict = PrivateAttr()
    _api_key: str = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._config = self._load_config()
        self._api_key = os.getenv("SERPER_API_KEY")
        if not self._api_key:
            raise ValueError("SERPER_API_KEY environment variable not set")
        self.logger.info("NewsScraperTool initialized with API key")

    def _load_config(self) -> Dict:
        """Load configuration from config.yaml."""
        with open("config.yaml", 'r') as f:
            return yaml.safe_load(f)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception as e:
            self.logger.error(f"Error extracting domain from URL {url}: {e}")
            return ""

    def _is_trusted_domain(self, url: str) -> bool:
        """Check if the domain is in the trusted domains list."""
        domain = self._extract_domain(url)
        trusted_domains = self._config['verification']['trusted_domains']
        return any(domain.endswith(trusted) for trusted in trusted_domains)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from Serper API."""
        try:
            if 'hour' in date_str or 'min' in date_str:
                # Handle relative time
                hours = int(date_str.split()[0]) if 'hour' in date_str else 0
                return datetime.now() - timedelta(hours=hours)
            elif 'day' in date_str:
                days = int(date_str.split()[0])
                return datetime.now() - timedelta(days=days)
            else:
                # Try parsing as absolute date
                return datetime.strptime(date_str, '%Y-%m-%d')
        except Exception as e:
            self.logger.error(f"Error parsing date {date_str}: {e}")
            return None

    def _fetch_articles(self, query: str) -> List[NewsArticle]:
        """Fetch articles from Serper API."""
        self.logger.info(f"Starting news fetch with query: {query}")
        
        headers = {
            "X-API-KEY": self._api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "type": "news",
            "num": 10
        }

        self.logger.info("Making Serper API request...")
        try:
            response = requests.post(
                self._config['api']['serper']['endpoint'],
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            self.logger.info(f"Serper API response status: {response.status_code}")
            self.logger.info(f"Raw response: {response.text[:1000]}...")  # Log first 1000 chars
            
            data = response.json()
            news_items = data.get('news', [])
            self.logger.info(f"Received {len(news_items)} news items")

            articles = []
            for item in news_items:
                domain = self._extract_domain(item['link'])
                self.logger.info(f"Processing article from domain: {domain}")
                
                if not self._is_trusted_domain(item['link']):
                    continue

                published_date = self._parse_date(item.get('date', ''))
                if not published_date:
                    continue

                lookback_hours = self._config['time_settings']['lookback_hours']
                if datetime.now() - published_date > timedelta(hours=lookback_hours):
                    continue

                article = NewsArticle(
                    title=item['title'],
                    url=item['link'],
                    source=item.get('source', domain),
                    published_date=published_date,
                    snippet=item.get('snippet', ''),
                )
                articles.append(article)

            self.logger.info(f"Successfully fetched {len(articles)} articles")
            return articles[:self._config['article_limits']['max_articles_per_day']]

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching news: {e}")
            return []

    def _run(self, query: str) -> str:
        """Run the news scraper tool."""
        articles = self._fetch_articles(query)
        
        if not articles:
            return "[]"
        
        # Convert articles to JSON-serializable format
        articles_data = []
        for article in articles:
            articles_data.append({
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "published_date": article.published_date.isoformat(),
                "snippet": article.snippet
            })
        
        return json.dumps(articles_data)

    def get_article_content(self, article: NewsArticle) -> Optional[str]:
        """Get the full content of an article (placeholder for future implementation)."""
        return None 