"""
Main entry point for the AI Daily Digest generator.
"""

import logging
from crew.ai_daily_crew import AIDailyCrew
from dotenv import load_dotenv
import os
import yaml
from pathlib import Path

def setup_logging():
    """Configure logging settings."""
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Ensure logs directory exists
    log_file = config['logging']['file']
    log_dir = os.path.dirname(log_file)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=config['logging']['file']
    )

def check_environment():
    """Verify all required environment variables are set."""
    required_vars = [
        'OPENAI_API_KEY',
        'SERPER_API_KEY'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

def main():
    """Main execution function."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Check environment
        check_environment()
        
        # Create and run the crew
        logger.info("Initializing AI Daily Digest generation...")
        crew = AIDailyCrew()
        digest = crew.run()
        
        logger.info("Digest generation completed successfully!")
        return digest
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    try:
        digest = main()
        print("\nDigest generated successfully!")
        print(f"Output: {digest}")
    except Exception as e:
        print(f"\nError: {e}")
        exit(1) 