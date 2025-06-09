#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
د کریپټو خبرونو بوټ - د تلیګرام لپاره
Crypto News Bot for Telegram with Pashto Translation
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

# د لاګنګ تنظیمات - Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# د Flask اپلیکیشن جوړول - Flask application setup
app = Flask(__name__)

class CryptoNewsBot:
    """د کریپټو خبرونو بوټ کلاس - Crypto News Bot Class"""
    
    def __init__(self, bot_token, channel_id):
        """د بوټ پیل کول - Bot initialization"""
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.rss_url = "https://cointelegraph.com/rss"
        self.translator = Translator()
        self.posted_articles = self.load_posted_articles()
        self.running = False
        
        # د تلیګرام API اساس URL - Telegram API base URL
        self.telegram_api_url = f"https://api.telegram.org/bot{bot_token}"
        
    def load_posted_articles(self):
        """د پخوانیو خبرونو ډېټا لوستل - Load previously posted articles data"""
        try:
            if os.path.exists('posted_articles.json'):
                with open('posted_articles.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"د {len(data)} پخوانیو خبرونو ډېټا لوستل شوه")
                    return data
            else:
                logger.info("د پخوانیو خبرونو ډېټا و نه موندل شوه، نوی پیل کوو")
                return {}
        except Exception as e:
            logger.error(f"د ډېټا لوستلو کې تیروتنه: {e}")
            return {}
    
    def save_posted_articles(self):
        """د خبرونو ډېټا ساتل - Save posted articles data"""
        try:
            with open('posted_articles.json', 'w', encoding='utf-8') as f:
                json.dump(self.posted_articles, f, indent=2, ensure_ascii=False)
            logger.debug("د خبرونو ډېټا په بریالیتوب سره وساتل شوه")
        except Exception as e:
            logger.error(f"د ډېټا ساتلو کې تیروتنه: {e}")
    
    def fetch_rss_news(self):
        """د RSS خبرونو راوړل - Fetch RSS news"""
        try:
            logger.info(f"د RSS خبرونو څانګه وړول: {self.rss_url}")
            
            # د RSS فیډ اخیستل - Fetch RSS feed
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoNewsBot/1.0)'
            }
            response = requests.get(self.rss_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # د RSS فیډ تحلیل - Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"د RSS فیډ تحلیل کې ستونزه: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries[:10]:  # د وروستیو ۱۰ خبرونو اخیستل - Get latest 10 articles
                article = {
                    'id': getattr(entry, 'id', entry.link),
                    'title': getattr(entry, 'title', 'سرلیک نشته'),
                    'link': getattr(entry, 'link', ''),
                    'published': getattr(entry, 'published', ''),
                    'published_parsed': getattr(entry, 'published_parsed', None)
                }
                articles.append(article)
            
            logger.info(f"په بریالیتوب سره {len(articles)} خبرونه واخیستل شول")
            return articles
            
        except Exception as e:
            logger.error(f"د RSS خبرونو اخیستلو کې تیروتنه: {e}")
            return []
    
    def translate_to_pashto(self, text):
        """د انګلیسي متن پښتو ته ژباړل - Translate English text to Pashto"""
        try:
            # د ګوګل ژباړې کارول - Using Google Translate
            translation = self.translator.translate(text, dest='ps', src='en')
            return translation.text
        except Exception as e:
            logger.error(f"د ژباړې کې تیروتنه: {e}")
            return f"[د ژباړې کې تیروتنه] {text}"
    
    def send_telegram_message(self, text):
        """د تلیګرام پیغام لېږل - Send Telegram message"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            data = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                logger.info("پیغام په بریالیتوب سره ولېږل شو")
                return True
            else:
                logger.error(f"د پیغام لېږلو کې تیروتنه: {result}")
                return False
                
        except Exception as e:
            logger.error(f"د تلیګرام پیغام لېږلو کې تیروتنه: {e}")
            return False
    
    def format_and_send_news(self, article):
        """د خبر تشکیل او لېږل - Format and send news"""
        try:
            title_en = article.get('title', 'سرلیک نشته')
            link = article.get('link', '')
            
            # د سرلیک پښتو ته ژباړل - Translate title to Pashto
            title_ps = self.translate_to_pashto(title_en)
            
            # د پیغام تشکیل - Format message
            message = f"""📰 {title_en}
📘 {title_ps}
🔗 {link}"""
            
            # د پیغام لېږل - Send message
            if self.send_telegram_message(message):
                # د خبر د لېږل شوي په توګه ثبتول - Mark article as posted
                article_id = article.get('id') or article.get('link', '')
                self.posted_articles[article_id] = {
                    'title': title_en,
                    'link': link,
                    'posted_at': datetime.now().isoformat()
                }
                self.save_posted_articles()
                logger.info(f"خبر په بریالیتوب سره ولېږل شو: {title_en[:50]}...")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"د خبر د تشکیل او لېږلو کې تیروتنه: {e}")
            return False
    
    def is_duplicate(self, article_id):
        """د تکراري خبر کتنه - Check for duplicate article"""
        return article_id in self.posted_articles
    
    def cleanup_old_entries(self, days=30):
        """د زړو ثبتونو پاکول - Clean up old entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            original_count = len(self.posted_articles)
            
            # د زړو ثبتونو فلټر کول - Filter out old entries
            self.posted_articles = {
                article_id: data for article_id, data in self.posted_articles.items()
                if datetime.fromisoformat(data.get('posted_at', '1970-01-01')) > cutoff_date
            }
            
            new_count = len(self.posted_articles)
            removed_count = original_count - new_count
            
            if removed_count > 0:
                self.save_posted_articles()
                logger.info(f"{removed_count} زړ ثبتونه پاک شول")
                
        except Exception as e:
            logger.error(f"د زړو ثبتونو پاکولو کې تیروتنه: {e}")
    
    def check_and_post_news(self):
        """د نویو خبرونو کتنه او لېږل - Check and post new news"""
        try:
            logger.info("د نویو کریپټو خبرونو کتنه...")
            
            # د RSS خبرونو اخیستل - Fetch RSS news
            articles = self.fetch_rss_news()
            
            if not articles:
                logger.warning("د RSS څانګې څخه خبرونه و نه موندل شول")
                return
            
            new_count = 0
            for article in articles:
                article_id = article.get('id') or article.get('link', '')
                
                # د تکراري خبر کتنه - Check for duplicate
                if not self.is_duplicate(article_id):
                    if self.format_and_send_news(article):
                        new_count += 1
                        # د بریښنايي محدودیت د مخنیوي لپاره ډنډ - Delay to prevent rate limiting
                        time.sleep(3)
            
            if new_count > 0:
                logger.info(f"{new_count} نوي خبرونه ولېږل شول")
            else:
                logger.info("د لېږلو لپاره نوي خبرونه و نه موندل شول")
                
        except Exception as e:
            logger.error(f"د خبرونو کتنې او لېږلو کې تیروتنه: {e}")
    
    def run_periodic_check(self):
        """د منظمو کتنو پرمخ وړل - Run periodic checks"""
        while self.running:
            try:
                # د خبرونو کتنه او لېږل - Check and post news
                self.check_and_post_news()
                
                # د ۱۰ دقیقو انتظار - Wait for 10 minutes (600 seconds)
                logger.info("د راتلونکې کتنې لپاره ۱۰ دقیقې انتظار...")
                time.sleep(600)
                
            except Exception as e:
                logger.error(f"د منظمې کتنې کې تیروتنه: {e}")
                # د تیروتنې په صورت کې ۱ دقیقې انتظار - Wait 1 minute on error
                time.sleep(60)
    
    def start(self):
        """د بوټ پیل کول - Start the bot"""
        logger.info("د کریپټو خبرونو بوټ پیلیږي...")
        
        # د تنظیماتو تصدیق - Validate configuration
        if not self.bot_token or self.bot_token == 'YOUR_BOT_TOKEN_HERE':
            logger.error("د بوټ ټوکن نه دی ورکړل شوی")
            return False
            
        if not self.channel_id or self.channel_id == '@YourChannelUsername':
            logger.error("د چینل پیژندګۍ نه دی ورکړل شوی")
            return False
        
        self.running = True
        
        # د لومړۍ کتنې ترسره کول - Perform initial check
        self.check_and_post_news()
        
        # د زړو ثبتونو پاکول - Clean up old entries
        self.cleanup_old_entries()
        
        # د منظمو کتنو پیل - Start periodic checks
        self.run_periodic_check()
        
        return True
    
    def stop(self):
        """د بوټ ودرول - Stop the bot"""
        logger.info("د کریپټو خبرونو بوټ ودریږي...")
        self.running = False

# د Flask د ژوندي ساتلو لپاره روټونه - Flask routes for keep-alive
@app.route('/')
def home():
    """د کور پاڼه - Home page"""
    return """
    <html>
    <head>
        <title>د کریپټو خبرونو بوټ - Crypto News Bot</title>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5;">
        <div style="max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50; text-align: center;">🤖 د کریپټو خبرونو بوټ</h1>
            <h2 style="color: #34495e; text-align: center;">Crypto News Bot</h2>
            
            <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0; color: #27ae60; font-weight: bold;">✅ بوټ فعال دی - Bot is Active</p>
            </div>
            
            <h3 style="color: #2c3e50;">ځانګړتیاوې - Features:</h3>
            <ul style="color: #555;">
                <li>د هرو ۱۰ دقیقو په موده کې د کریپټو خبرونو کتنه</li>
                <li>د انګلیسي څخه پښتو ته ژباړه</li>
                <li>د تکراري خبرونو مخنیوی</li>
                <li>د تلیګرام چینل ته اتوماتیک لېږل</li>
            </ul>
            
            <h3 style="color: #2c3e50;">Features:</h3>
            <ul style="color: #555;">
                <li>Monitors crypto news every 10 minutes</li>
                <li>Translates English to Pashto</li>
                <li>Prevents duplicate posts</li>
                <li>Automatic posting to Telegram channel</li>
            </ul>
            
            <p style="text-align: center; margin-top: 30px; color: #7f8c8d;">
                د Cointelegraph RSS څخه خبرونه اخلي<br>
                Powered by Cointelegraph RSS
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """د روغتیا کتنې پاڼه - Health check endpoint"""
    return {'status': 'ok', 'message': 'د کریپټو خبرونو بوټ فعال دی'}

def run_flask():
    """د Flask سرور پرمخ وړل - Run Flask server"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"د Flask سرور کې تیروتنه: {e}")

def run_bot():
    """د بوټ پرمخ وړل - Run the bot"""
    try:
        # دلته خپل بوټ ټوکن او د چینل پیژندګۍ ورکړئ
        # Enter your bot token and channel ID here
        BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # دلته خپل بوټ ټوکن ورکړئ
        CHANNEL_ID = '@YourChannelUsername'  # دلته د خپل چینل پیژندګۍ ورکړئ
        
        bot = CryptoNewsBot(BOT_TOKEN, CHANNEL_ID)
        bot.start()
    except Exception as e:
        logger.error(f"د بوټ کې تیروتنه: {e}")
        # د تیروتنې وروسته د ۶۰ ثانیو انتظار - Wait 60 seconds after error
        time.sleep(60)
        run_bot()

if __name__ == "__main__":
    logger.info("د کریپټو خبرونو بوټ پیلیږي...")
    
    # د Flask سرور په شاليد کې پیل کول - Start Flask server in background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # د بوټ په اصلي thread کې پیل کول - Start bot in main thread
    run_bot()