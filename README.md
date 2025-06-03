# AI Daily Digest 🤖📰

An automated system that generates daily digests of AI-related news using a multi-agent approach powered by CrewAI.

## Overview

AI Daily Digest automatically fetches, summarizes, verifies, and compiles the most relevant AI news stories from the past 24 hours. The system uses multiple specialized agents working together to produce high-quality, verified news digests.

## Features

- Automated news harvesting from multiple sources
- Intelligent article summarization
- Fact verification against trusted sources
- Professional formatting and compilation
- Daily automated digests

## Project Structure

```
.
├── agents/
│   ├── harvester_agent.py     # Gathers news articles
│   ├── summarizer_agent.py    # Summarizes articles
│   ├── verifier_agent.py      # Verifies claims
│   └── editor_agent.py        # Compiles final digest
├── tools/
│   ├── news_scraper_tool.py   # News API integration
│   └── search_tool.py         # Search verification
├── crew/
│   └── ai_daily_crew.py       # CrewAI orchestration
├── main.py                    # Entry point
├── config.yaml                # Configuration
└── README.md                  # Documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai_daily_digest.git
cd ai_daily_digest
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Run the digest generator:

```bash
python main.py
```

## Configuration

Edit `config.yaml` to customize:
- News sources
- Output format preferences
- Update frequency
- API configurations

## Requirements

- Python 3.9+
- CrewAI 0.27+
- OpenAI API key
- Serper.dev API key (or alternative news API)
