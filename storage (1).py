"""
Simple file-based storage for tracking posted news articles.
Prevents duplicate posting by maintaining a record of posted article IDs.
"""

import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsStorage:
    """Handles storage and retrieval of posted news data"""
    
    def __init__(self, storage_file='posted_news.json'):
        self.storage_file = storage_file
        self.posted_articles = self._load_storage()
    
    def _load_storage(self):
        """Load posted articles data from JSON file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded {len(data)} posted articles from storage")
                    return data
            else:
                logger.info("No existing storage file found, starting fresh")
                return {}
        except Exception as e:
            logger.error(f"Error loading storage: {e}")
            return {}
    
    def _save_storage(self):
        """Save posted articles data to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.posted_articles, f, indent=2, ensure_ascii=False)
            logger.debug("Storage saved successfully")
        except Exception as e:
            logger.error(f"Error saving storage: {e}")
    
    def is_duplicate(self, article_id):
        """
        Check if article has already been posted
        
        Args:
            article_id (str): Unique identifier for the article
            
        Returns:
            bool: True if article was already posted, False otherwise
        """
        return article_id in self.posted_articles
    
    def mark_as_posted(self, article_id, article_data):
        """
        Mark article as posted
        
        Args:
            article_id (str): Unique identifier for the article
            article_data (dict): Article information
        """
        try:
            self.posted_articles[article_id] = {
                'title': article_data.get('title', ''),
                'link': article_data.get('link', ''),
                'posted_at': datetime.now().isoformat(),
                'published': article_data.get('published', '')
            }
            self._save_storage()
            logger.debug(f"Marked article as posted: {article_id}")
        except Exception as e:
            logger.error(f"Error marking article as posted: {e}")
    
    def cleanup_old_entries(self, days=30):
        """
        Remove old entries from storage to prevent unlimited growth
        
        Args:
            days (int): Number of days to keep entries
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            original_count = len(self.posted_articles)
            
            # Filter out old entries
            self.posted_articles = {
                article_id: data for article_id, data in self.posted_articles.items()
                if datetime.fromisoformat(data.get('posted_at', '1970-01-01')) > cutoff_date
            }
            
            new_count = len(self.posted_articles)
            removed_count = original_count - new_count
            
            if removed_count > 0:
                self._save_storage()
                logger.info(f"Cleaned up {removed_count} old entries from storage")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_stats(self):
        """Get storage statistics"""
        return {
            'total_posted': len(self.posted_articles),
            'storage_file': self.storage_file,
            'file_exists': os.path.exists(self.storage_file)
        }
