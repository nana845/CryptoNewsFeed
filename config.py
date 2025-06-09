"""
Configuration management for the Telegram crypto news bot.
Handles environment variables and default settings.
"""

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Telegram Bot Configuration
        self.BOT_TOKEN = os.getenv('BOT_TOKEN', '')
        self.CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME', '@MyCryptoNewsChannel')
        
        # RSS Feed Configuration
        self.RSS_URL = os.getenv('RSS_URL', 'https://cointelegraph.com/rss')
        
        # Bot Behavior Configuration
        self.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '600'))  # 10 minutes
        self.MAX_ARTICLES_PER_CHECK = int(os.getenv('MAX_ARTICLES_PER_CHECK', '10'))
        
        # Storage Configuration
        self.STORAGE_FILE = os.getenv('STORAGE_FILE', 'posted_news.json')
        self.CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', '30'))
        
        # Logging Configuration
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.LOG_LEVEL = getattr(logging, log_level, logging.INFO)
        
        # Validate critical configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate critical configuration values"""
        if not self.BOT_TOKEN:
            logger.warning("BOT_TOKEN not set in environment variables")
        
        if not self.CHANNEL_USERNAME.startswith('@'):
            logger.warning(f"CHANNEL_USERNAME should start with @: {self.CHANNEL_USERNAME}")
        
        if self.CHECK_INTERVAL < 60:
            logger.warning(f"CHECK_INTERVAL is very low ({self.CHECK_INTERVAL}s), consider increasing")
        
        logger.info(f"Configuration loaded:")
        logger.info(f"  RSS URL: {self.RSS_URL}")
        logger.info(f"  Channel: {self.CHANNEL_USERNAME}")
        logger.info(f"  Check interval: {self.CHECK_INTERVAL}s")
        logger.info(f"  Max articles per check: {self.MAX_ARTICLES_PER_CHECK}")
    
    def get_env_template(self):
        """Get environment variables template for documentation"""
        return """
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
CHANNEL_USERNAME=@YourChannelUsername

# RSS Feed Configuration (optional)
RSS_URL=https://cointelegraph.com/rss

# Bot Behavior (optional)
CHECK_INTERVAL=600
MAX_ARTICLES_PER_CHECK=10

# Storage (optional)
STORAGE_FILE=posted_news.json
CLEANUP_DAYS=30

# Logging (optional)
LOG_LEVEL=INFO
        """.strip()
