#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
د کریپټو خبرونو تلیګرام بوټ - د پښتو او انګلیسي دواړو ژبو سره
Telegram Crypto News Bot with Pashto and English Support
"""

import os
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from flask import Flask
import feedparser
import requests
from googletrans import Translator

# د لاګنګ تنظیمات - Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# د Flask اپلیکیشن جوړول - Flask Application Creation
app = Flask(__name__)

class TelegramCryptoBot:
    """د کریپټو خبرونو تلیګرام بوټ کلاس - Telegram Crypto News Bot Class"""
    
    def __init__(self):
        """د بوټ پیل کول او تنظیمات - Bot Initialization and Configuration"""
        # د چاپیریال متغیرونو څخه تنظیمات اخیستل - Loading settings from environment variables
        self.bot_token = os.getenv('BOT_TOKEN')
        self.channel_id = os.getenv('CHANNEL_ID')
        
        # د RSS تنظیمات - RSS Configuration
        self.rss_url = "https://cointelegraph.com/rss"
        self.max_articles = 10  # د اخیستلو د خبرونو شمیر - Number of articles to fetch
        self.check_interval = 600  # ۱۰ دقیقې - 10 minutes in seconds
        
        # د ژباړې خدماتو پیل - Translation Service Initialization
        self.translator = Translator()
        
        # د لېږل شویو خبرونو ډېټابیس - Posted Articles Database
        self.storage_file = 'posted_articles.json'
        self.posted_articles = self.load_posted_articles()
        
        # د بوټ حالت - Bot Status
        self.running = False
        
        # د تلیګرام API ادرس - Telegram API URL
        self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # د تنظیماتو تصدیق - Configuration Validation
        self.validate_configuration()
    
    def validate_configuration(self):
        """د تنظیماتو تصدیق کول - Configuration Validation"""
        if not self.bot_token:
            logger.error("BOT_TOKEN د چاپیریال متغیر نه دی ټاکل شوی - BOT_TOKEN environment variable not set")
            raise ValueError("BOT_TOKEN د چاپیریال متغیر ضروری دی - BOT_TOKEN environment variable is required")
        
        if not self.channel_id:
            logger.error("CHANNEL_ID د چاپیریال متغیر نه دی ټاکل شوی - CHANNEL_ID environment variable not set")
            raise ValueError("CHANNEL_ID د چاپیریال متغیر ضروری دی - CHANNEL_ID environment variable is required")
        
        if not self.channel_id.startswith('@') and not self.channel_id.startswith('-'):
            logger.error("CHANNEL_ID باید د @ سره پیل شي یا د چینل ID وي - CHANNEL_ID must start with @ or be a channel ID")
            raise ValueError("CHANNEL_ID باید د @ سره پیل شي - CHANNEL_ID must start with @")
        
        logger.info(f"تنظیمات تصدیق شول - Configuration validated:")
        logger.info(f"  چینل: {self.channel_id} - Channel: {self.channel_id}")
        logger.info(f"  RSS لینک: {self.rss_url} - RSS URL: {self.rss_url}")
        logger.info(f"  د کتنې موده: {self.check_interval} ثانیې - Check interval: {self.check_interval} seconds")
    
    def load_posted_articles(self):
        """د لېږل شویو خبرونو ډېټا لوستل - Load Posted Articles Data"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    logger.info(f"د {len(data)} پخوانیو خبرونو ډېټا لوستل شوه - Loaded {len(data)} previously posted articles")
                    return data
            else:
                logger.info("د پخوانیو خبرونو فایل و نه موندل شو، نوی پیل کوو - No previous articles file found, starting fresh")
                return {}
        except Exception as e:
            logger.error(f"د ډېټا لوستلو کې تیروتنه: {e} - Error loading data: {e}")
            return {}
    
    def save_posted_articles(self):
        """د لېږل شویو خبرونو ډېټا ساتل - Save Posted Articles Data"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as file:
                json.dump(self.posted_articles, file, indent=2, ensure_ascii=False)
            logger.debug("د خبرونو ډېټا بریالیتوب سره وساتل شوه - Articles data saved successfully")
        except Exception as e:
            logger.error(f"د ډېټا ساتلو کې تیروتنه: {e} - Error saving data: {e}")
    
    def cleanup_old_entries(self, days=30):
        """د زړو ثبتونو پاکول - Clean Up Old Entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            original_count = len(self.posted_articles)
            
            # د زړو ثبتونو فلټر کول - Filter out old entries
            self.posted_articles = {
                article_id: data for article_id, data in self.posted_articles.items()
                if datetime.fromisoformat(data.get('posted_at', '1970-01-01T00:00:00')) > cutoff_date
            }
            
            new_count = len(self.posted_articles)
            removed_count = original_count - new_count
            
            if removed_count > 0:
                self.save_posted_articles()
                logger.info(f"{removed_count} زړ ثبتونه پاک شول - {removed_count} old entries cleaned up")
            else:
                logger.info("د پاکولو لپاره زړ ثبتونه و نه موندل شول - No old entries found for cleanup")
                
        except Exception as e:
            logger.error(f"د زړو ثبتونو پاکولو کې تیروتنه: {e} - Error during cleanup: {e}")
    
    def fetch_rss_articles(self):
        """د RSS څخه خبرونو اخیستل - Fetch Articles from RSS"""
        try:
            logger.info(f"د RSS څخه خبرونو اخیستل: {self.rss_url} - Fetching articles from RSS: {self.rss_url}")
            
            # د غوښتنې سرلیکونه - Request headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; TelegramCryptoBot/1.0; +https://t.me/your_bot)',
                'Accept': 'application/rss+xml, application/xml, text/xml'
            }
            
            # د RSS فیډ اخیستل - Fetch RSS feed
            response = requests.get(self.rss_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # د RSS فیډ تحلیل - Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"د RSS فیډ تحلیل کې ستونزه: {feed.bozo_exception} - RSS feed parsing issue: {feed.bozo_exception}")
            
            # د خبرونو لیست جوړول - Create articles list
            articles = []
            for entry in feed.entries[:self.max_articles]:
                article = {
                    'id': getattr(entry, 'id', entry.link),
                    'title': getattr(entry, 'title', 'سرلیک نشته - No title'),
                    'link': getattr(entry, 'link', ''),
                    'published': getattr(entry, 'published', ''),
                    'published_parsed': getattr(entry, 'published_parsed', None),
                    'summary': getattr(entry, 'summary', '')
                }
                
                # د خالي یا نامعلومه لینک څخه مخنیوی - Prevent empty or invalid links
                if article['link'] and article['title'] != 'سرلیک نشته - No title':
                    articles.append(article)
            
            logger.info(f"بریالیتوب سره {len(articles)} خبرونه واخیستل شول - Successfully fetched {len(articles)} articles")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"د RSS اخیستلو کې د شبکې تیروتنه: {e} - Network error fetching RSS: {e}")
            return []
        except Exception as e:
            logger.error(f"د RSS تحلیل کې تیروتنه: {e} - Error parsing RSS: {e}")
            return []
    
    def translate_to_pashto(self, text):
        """د انګلیسي متن پښتو ته ژباړل - Translate English Text to Pashto"""
        try:
            # د ګوګل ژباړې خدماتو کارول - Using Google Translate services
            translation = self.translator.translate(text, dest='ps', src='en')
            
            if translation and translation.text:
                logger.debug(f"ژباړه بریالۍ وه - Translation successful: {text[:50]}... -> {translation.text[:50]}...")
                return translation.text
            else:
                logger.warning(f"د ژباړې خدماتو څخه تش ځواب - Empty response from translation service")
                return f"[د ژباړې کې ستونزه] {text}"
                
        except Exception as e:
            logger.error(f"د ژباړې کې تیروتنه: {e} - Translation error: {e}")
            return f"[د ژباړې کې ستونزه - Translation Error] {text}"
    
    def send_telegram_message(self, text):
        """د تلیګرام پیغام لېږل - Send Telegram Message"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            
            # د پیغام ډېټا - Message data
            payload = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False,
                'disable_notification': False
            }
            
            # د پیغام لېږل - Send message
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                logger.info("پیغام بریالیتوب سره ولېږل شو - Message sent successfully")
                return True
            else:
                logger.error(f"د پیغام لېږلو کې تیروتنه: {result} - Error sending message: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"د تلیګرام API کې د شبکې تیروتنه: {e} - Network error with Telegram API: {e}")
            return False
        except Exception as e:
            logger.error(f"د پیغام لېږلو کې عمومي تیروتنه: {e} - General error sending message: {e}")
            return False
    
    def format_news_message(self, article):
        """د خبر د پیغام تشکیل - Format News Message"""
        title_en = article.get('title', 'سرلیک نشته - No title')
        link = article.get('link', '')
        
        # د سرلیک پښتو ته ژباړل - Translate title to Pashto
        title_ps = self.translate_to_pashto(title_en)
        
        # د پیغام تشکیل - Format message according to requirements
        message = f"""📰 {title_en}
📘 {title_ps}
🔗 {link}"""
        
        return message
    
    def is_article_posted(self, article_id):
        """د خبر د لېږل شوي کیدو کتنه - Check if Article was Posted"""
        return article_id in self.posted_articles
    
    def mark_article_as_posted(self, article):
        """د خبر د لېږل شوي په توګه ثبتول - Mark Article as Posted"""
        article_id = article.get('id') or article.get('link', '')
        
        self.posted_articles[article_id] = {
            'title': article.get('title', ''),
            'link': article.get('link', ''),
            'posted_at': datetime.now().isoformat(),
            'published': article.get('published', '')
        }
        
        self.save_posted_articles()
        logger.debug(f"خبر د لېږل شوي په توګه وثبت شو - Article marked as posted: {article_id}")
    
    def process_and_post_article(self, article):
        """د خبر پروسس کول او لېږل - Process and Post Article"""
        try:
            # د پیغام تشکیل - Format message
            message = self.format_news_message(article)
            
            # د پیغام لېږل - Send message
            if self.send_telegram_message(message):
                # د خبر د لېږل شوي په توګه ثبتول - Mark article as posted
                self.mark_article_as_posted(article)
                
                title_preview = article.get('title', '')[:50]
                logger.info(f"خبر بریالیتوب سره ولېږل شو - Article posted successfully: {title_preview}...")
                return True
            else:
                logger.error(f"د خبر لېږلو کې ناکامي - Failed to post article: {article.get('title', '')[:50]}...")
                return False
                
        except Exception as e:
            logger.error(f"د خبر پروسس کولو کې تیروتنه: {e} - Error processing article: {e}")
            return False
    
    def check_and_post_new_articles(self):
        """د نویو خبرونو کتنه او لېږل - Check and Post New Articles"""
        try:
            logger.info("د نویو کریپټو خبرونو کتنه پیل شوه - Starting check for new crypto articles")
            
            # د RSS څخه خبرونو اخیستل - Fetch articles from RSS
            articles = self.fetch_rss_articles()
            
            if not articles:
                logger.warning("د RSS څخه خبرونه و نه موندل شول - No articles found from RSS")
                return
            
            # د نویو خبرونو شمیرنه - Count new articles
            new_articles_count = 0
            
            for article in articles:
                article_id = article.get('id') or article.get('link', '')
                
                # د تکراري خبر کتنه - Check for duplicate article
                if not self.is_article_posted(article_id):
                    if self.process_and_post_article(article):
                        new_articles_count += 1
                        # د نرخ محدودیت څخه مخنیوی لپاره ډنډ - Delay to prevent rate limiting
                        time.sleep(2)
                else:
                    logger.debug(f"خبر دمخه لېږل شوی: {article.get('title', '')[:30]}... - Article already posted")
            
            if new_articles_count > 0:
                logger.info(f"{new_articles_count} نوي خبرونه بریالیتوب سره ولېږل شول - {new_articles_count} new articles posted successfully")
            else:
                logger.info("د لېږلو لپاره نوي خبرونه و نه موندل شول - No new articles found to post")
                
        except Exception as e:
            logger.error(f"د خبرونو کتنې او لېږلو کې تیروتنه: {e} - Error checking and posting articles: {e}")
    
    def run_periodic_checks(self):
        """د منظمو کتنو پرمخ وړل - Run Periodic Checks"""
        logger.info("د منظمو کتنو پروسه پیل شوه - Periodic checks process started")
        
        while self.running:
            try:
                # د خبرونو کتنه او لېږل - Check and post articles
                self.check_and_post_new_articles()
                
                # د هر ۲۴ ساعتونو څخه وروسته د زړو ثبتونو پاکول - Clean up old entries after every 24 hours
                current_time = datetime.now()
                if not hasattr(self, 'last_cleanup') or (current_time - self.last_cleanup).total_seconds() > 86400:
                    self.cleanup_old_entries()
                    self.last_cleanup = current_time
                
                # د راتلونکي کتنې لپاره انتظار - Wait for next check
                logger.info(f"د راتلونکې کتنې لپاره {self.check_interval} ثانیې انتظار - Waiting {self.check_interval} seconds for next check")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("د کیبورډ څخه ودرولو غوښتنه ترلاسه شوه - Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"د منظمې کتنې کې تیروتنه: {e} - Error in periodic check: {e}")
                # د تیروتنې په صورت کې ۶۰ ثانیې انتظار - Wait 60 seconds on error
                time.sleep(60)
    
    def start(self):
        """د بوټ پیل کول - Start the Bot"""
        logger.info("🚀 د کریپټو خبرونو تلیګرام بوټ پیلیږي - Starting Telegram Crypto News Bot")
        
        try:
            # د لومړۍ کتنې ترسره کول - Perform initial check
            logger.info("د لومړۍ کتنې ترسره کول - Performing initial check")
            self.check_and_post_new_articles()
            
            # د زړو ثبتونو پاکول - Clean up old entries
            self.cleanup_old_entries()
            self.last_cleanup = datetime.now()
            
            # د بوټ د دوامداره کار لپاره تنظیم - Set bot for continuous operation
            self.running = True
            
            # د منظمو کتنو پیل - Start periodic checks
            self.run_periodic_checks()
            
        except Exception as e:
            logger.error(f"د بوټ د پیل کولو کې تیروتنه: {e} - Error starting bot: {e}")
            raise
    
    def stop(self):
        """د بوټ ودرول - Stop the Bot"""
        logger.info("د کریپټو خبرونو بوټ ودریږي - Stopping Crypto News Bot")
        self.running = False

# د Flask د ژوندي ساتلو روټونه - Flask Keep-Alive Routes
@app.route('/')
def home():
    """د کور پاڼه - Home Page"""
    return """
    <!DOCTYPE html>
    <html lang="ps">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>د کریپټو خبرونو تلیګرام بوټ - Telegram Crypto News Bot</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; font-size: 2.5em; }
            .status { background: linear-gradient(45deg, #27ae60, #2ecc71); color: white; padding: 15px; border-radius: 10px; text-align: center; margin: 20px 0; font-weight: bold; font-size: 1.2em; }
            .feature { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #3498db; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
            ul { line-height: 1.8; }
            .footer { text-align: center; margin-top: 30px; color: #7f8c8d; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 د کریپټو خبرونو تلیګرام بوټ</h1>
            <h2 style="text-align: center; color: #34495e;">Telegram Crypto News Bot</h2>
            
            <div class="status">
                ✅ بوټ فعال دی او کار کوي - Bot is Active and Running
            </div>
            
            <div class="feature">
                <h3>🔍 د بوټ ځانګړتیاوې - Bot Features:</h3>
                <ul>
                    <li>د هرو ۱۰ دقیقو په موده کې د Cointelegraph څخه د کریپټو خبرونو اخیستل</li>
                    <li>د انګلیسي څخه پښتو ته د سرلیکونو ژباړه</li>
                    <li>د تکراري خبرونو مخنیوی</li>
                    <li>د تلیګرام چینل ته اتوماتیک لېږل</li>
                    <li>د زړو ثبتونو اتوماتیک پاکول (۳۰ ورځې)</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🌐 Bot Features:</h3>
                <ul>
                    <li>Fetches crypto news from Cointelegraph every 10 minutes</li>
                    <li>Translates English titles to Pashto</li>
                    <li>Prevents duplicate posts</li>
                    <li>Automatic posting to Telegram channel</li>
                    <li>Automatic cleanup of old entries (30 days)</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>📋 د پیغام بڼه - Message Format:</h3>
                <pre style="background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px;">📰 English Title
📘 د پښتو سرلیک
🔗 https://article-link.com</pre>
            </div>
            
            <div class="footer">
                <p>🔄 وروستی ځل تازه شوی: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ UTC</p>
                <p>Last Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ UTC</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """د روغتیا کتنې پاڼه - Health Check Endpoint"""
    return {
        'status': 'ok',
        'message': 'د کریپټو خبرونو بوټ فعال دی - Crypto News Bot is running',
        'timestamp': datetime.now().isoformat(),
        'service': 'telegram-crypto-news-bot'
    }

@app.route('/stats')
def stats():
    """د احصایو پاڼه - Statistics Endpoint"""
    try:
        if os.path.exists('posted_articles.json'):
            with open('posted_articles.json', 'r', encoding='utf-8') as f:
                posted_data = json.load(f)
                return {
                    'total_posted_articles': len(posted_data),
                    'last_check': datetime.now().isoformat(),
                    'storage_file_exists': True
                }
        else:
            return {
                'total_posted_articles': 0,
                'last_check': datetime.now().isoformat(),
                'storage_file_exists': False
            }
    except Exception as e:
        return {'error': str(e)}

def run_flask_server():
    """د Flask سرور پرمخ وړل - Run Flask Server"""
    try:
        logger.info("د Flask سرور پیل کول - Starting Flask server")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"د Flask سرور کې تیروتنه: {e} - Flask server error: {e}")

def run_telegram_bot():
    """د تلیګرام بوټ پرمخ وړل - Run Telegram Bot"""
    try:
        # د بوټ جوړول او پیل کول - Create and start bot
        bot = TelegramCryptoBot()
        bot.start()
    except Exception as e:
        logger.error(f"د تلیګرام بوټ کې تیروتنه: {e} - Telegram bot error: {e}")
        # د تیروتنې وروسته د ۶۰ ثانیو انتظار - Wait 60 seconds after error
        time.sleep(60)
        # د بوټ بیا پیل کول - Restart bot
        run_telegram_bot()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 د کریپټو خبرونو تلیګرام بوټ پیل کول - Starting Telegram Crypto News Bot")
    logger.info("=" * 60)
    
    # د Flask سرور په شالید کې پیل کول - Start Flask server in background
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask سرور په شالید کې پیل شو - Flask server started in background")
    
    # د تلیګرام بوټ په اصلي thread کې پیل کول - Start Telegram bot in main thread
    run_telegram_bot()