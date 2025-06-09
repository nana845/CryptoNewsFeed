"""
Telegram bot implementation for crypto news posting.
Handles RSS feed checking and message posting to Telegram channels.
"""

import time
import threading
import logging
from datetime import datetime
from rss_fetcher import RSSFetcher
from storage import NewsStorage
from config import Config
import requests
from googletrans import Translator

logger = logging.getLogger(__name__)

class TelegramAPI:
    """Handles Telegram Bot API interactions"""
    
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Send message to Telegram chat/channel"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': False
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send message to Telegram: {e}")
            return None

class CryptoNewsBot:
    """Main bot class that coordinates RSS fetching and Telegram posting"""
    
    def __init__(self):
        self.config = Config()
        self.rss_fetcher = RSSFetcher(self.config.RSS_URL)
        self.storage = NewsStorage()
        self.telegram = TelegramAPI(self.config.BOT_TOKEN)
        self.translator = Translator()
        self.running = False
        
    def translate_to_pashto(self, text):
        """Translate text to Pashto using Google Translate"""
        try:
            # Google Translate API call to translate to Pashto
            translation = self.translator.translate(text, dest='ps', src='en')
            return translation.text
        except Exception as e:
            logger.error(f"Translation error: {e}")
            # Return original text if translation fails
            return f"[Translation unavailable] {text}"
    
    def format_news_message(self, article):
        """Format article data into Telegram message with English and Pashto"""
        title_en = article.get('title', 'No title')
        link = article.get('link', '')
        
        # Translate title to Pashto
        title_ps = self.translate_to_pashto(title_en)
        
        # Create message with new format: English title, Pashto title, link
        message = f"""
📰 {title_en}
📘 {title_ps}
🔗 {link}
        """.strip()
        
        return message
    
    def post_article(self, article):
        """Post single article to Telegram channel"""
        try:
            message = self.format_news_message(article)
            result = self.telegram.send_message(
                self.config.CHANNEL_USERNAME, 
                message
            )
            
            if result and result.get('ok'):
                logger.info(f"Successfully posted: {article.get('title', 'Unknown')}")
                return True
            else:
                logger.error(f"Failed to post article: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error posting article: {e}")
            return False
    
    def check_and_post_news(self):
        """Check RSS feed and post new articles"""
        try:
            logger.info("Checking for new crypto news...")
            articles = self.rss_fetcher.fetch_latest()
            
            if not articles:
                logger.warning("No articles fetched from RSS feed")
                return
            
            new_count = 0
            for article in articles:
                article_id = article.get('id') or article.get('link', '')
                
                if not self.storage.is_duplicate(article_id):
                    if self.post_article(article):
                        self.storage.mark_as_posted(article_id, article)
                        new_count += 1
                        # Add delay between posts to avoid rate limiting
                        time.sleep(2)
            
            if new_count > 0:
                logger.info(f"Posted {new_count} new articles")
            else:
                logger.info("No new articles to post")
                
        except Exception as e:
            logger.error(f"Error in check_and_post_news: {e}")
    
    def run_periodic_check(self):
        """Run periodic RSS checks every 10 minutes"""
        while self.running:
            try:
                self.check_and_post_news()
                # Wait 10 minutes (600 seconds)
                time.sleep(600)
            except Exception as e:
                logger.error(f"Error in periodic check: {e}")
                # Wait 1 minute before retrying on error
                time.sleep(60)
    
    def start(self):
        """Start the bot"""
        logger.info("Starting Crypto News Bot...")
        
        # Validate configuration
        if not self.config.BOT_TOKEN:
            logger.error("BOT_TOKEN not configured")
            return
            
        if not self.config.CHANNEL_USERNAME:
            logger.error("CHANNEL_USERNAME not configured")
            return
        
        self.running = True
        
        # Do initial check
        self.check_and_post_news()
        
        # Start periodic checking
        self.run_periodic_check()
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping Crypto News Bot...")
        self.running = False
