#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
د کریپټو خبرونو تلیګرام بوټ - اصلي فایل
Telegram Crypto News Bot - Main File
د UptimeRobot سره د 24/7 فعالیت لپاره
"""

import os
import json
import time
import threading
import logging
import re
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template_string
import feedparser
import requests
from googletrans import Translator
# OpenAI import - will be used if available

# د لاګنګ تنظیمات - Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# د Flask app جوړول - Flask app creation
app = Flask(__name__)

class CryptoNewsBot:
    """د کریپټو خبرونو تلیګرام بوټ کلاس - Telegram Crypto News Bot Class"""
    
    def __init__(self):
        """د بوټ پیل کول - Bot initialization"""
        # د چاپیریال متغیرونو څخه تنظیمات - Settings from environment variables
        self.bot_token = os.getenv('BOT_TOKEN')
        self.channel_username = os.getenv('CHANNEL_USERNAME') or os.getenv('CHANNEL_ID')
        
        # د RSS فیډ URL - RSS feed URL
        self.rss_url = "https://cointelegraph.com/rss"
        
        # د ژباړې خدماتو جوړول - Translation service setup
        self.translator = Translator()
        
        # د OpenAI client پیل کول - Initialize OpenAI client
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_client = None
        
        if self.openai_api_key:
            try:
                import openai
                openai.api_key = self.openai_api_key
                self.openai_client = openai
                logger.info("د OpenAI client بریالیتوب سره تنظیم شو - OpenAI client configured successfully")
            except ImportError:
                logger.warning("د OpenAI library نشته - OpenAI library not available")
            except Exception as e:
                logger.error(f"د OpenAI تنظیم کې تیروتنه: {e} - OpenAI setup error: {e}")
        else:
            logger.warning("د OpenAI API key نشته - OpenAI API key not provided")
        
        # د ډېټا ساتنې فایل - Data storage file
        self.storage_file = 'posted_articles.json'
        self.posted_articles = self.load_posted_articles()
        
        # د بوټ حالت - Bot status
        self.running = False
        
        # د تلیګرام API URL - Telegram API URL
        if self.bot_token:
            self.telegram_api_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # د تنظیماتو تصدیق - Configuration validation
        self.validate_config()
    
    def validate_config(self):
        """د تنظیماتو تصدیق - Configuration validation"""
        if not self.bot_token:
            logger.error("BOT_TOKEN د چاپیریال متغیر نه دی ورکړل شوی - BOT_TOKEN environment variable not provided")
            return False
        
        if not self.channel_username:
            logger.error("CHANNEL_USERNAME/CHANNEL_ID د چاپیریال متغیر نه دی ورکړل شوی - CHANNEL_USERNAME/CHANNEL_ID environment variable not provided")
            return False
        
        # د چینل نوم سمول - Channel name correction
        if self.channel_username.startswith('https://t.me/'):
            # د بشپړ URL څخه یوازې د چینل نوم اخیستل - Extract channel name from full URL
            channel_name = self.channel_username.split('/')[-1]
            self.channel_username = f"@{channel_name}"
        elif not self.channel_username.startswith('@') and not self.channel_username.startswith('-'):
            self.channel_username = f"@{self.channel_username}"
        
        # د اضافي @ نښو پاکول - Remove extra @ symbols
        if self.channel_username.startswith('@@'):
            self.channel_username = self.channel_username[1:]
        
        logger.info(f"د بوټ تنظیمات تصدیق شول - Bot configuration validated")
        logger.info(f"چینل: {self.channel_username} - Channel: {self.channel_username}")
        return True
    
    def load_posted_articles(self):
        """د لېږل شویو خبرونو ډېټا لوستل - Load posted articles data"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"د {len(data)} پخوانیو خبرونو ډېټا لوستل شوه - Loaded {len(data)} previous articles")
                    return data
            else:
                logger.info("د پخوانیو خبرونو فایل نه موجود - No previous articles file found")
                return {}
        except Exception as e:
            logger.error(f"د ډېټا لوستلو کې تیروتنه: {e} - Error loading data: {e}")
            return {}
    
    def save_posted_articles(self):
        """د لېږل شویو خبرونو ډېټا ساتل - Save posted articles data"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.posted_articles, f, indent=2, ensure_ascii=False)
            logger.debug("د خبرونو ډېټا وساتل شوه - Articles data saved")
        except Exception as e:
            logger.error(f"د ډېټا ساتلو کې تیروتنه: {e} - Error saving data: {e}")
    
    def cleanup_old_entries(self, days=30):
        """د زړو ثبتونو پاکول - Clean up old entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            original_count = len(self.posted_articles)
            
            # د زړو ثبتونو فلټر کول - Filter old entries
            self.posted_articles = {
                article_id: data for article_id, data in self.posted_articles.items()
                if datetime.fromisoformat(data.get('posted_at', '1970-01-01T00:00:00')) > cutoff_date
            }
            
            removed_count = original_count - len(self.posted_articles)
            if removed_count > 0:
                self.save_posted_articles()
                logger.info(f"{removed_count} زړ ثبتونه پاک شول - {removed_count} old entries cleaned")
        except Exception as e:
            logger.error(f"د زړو ثبتونو پاکولو کې تیروتنه: {e} - Error cleaning old entries: {e}")
    
    def fetch_rss_news(self):
        """د RSS څخه خبرونو اخیستل - Fetch news from RSS"""
        try:
            logger.info(f"د RSS څخه خبرونو اخیستل - Fetching news from RSS: {self.rss_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; CryptoNewsBot/1.0)'
            }
            
            response = requests.get(self.rss_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"د RSS تحلیل کې ستونزه - RSS parsing issue: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries[:10]:  # د وروستیو ۱۰ خبرونو اخیستل - Get latest 10 articles
                article = {
                    'id': getattr(entry, 'id', entry.link),
                    'title': getattr(entry, 'title', 'No title'),
                    'link': getattr(entry, 'link', ''),
                    'published': getattr(entry, 'published', ''),
                    'summary': getattr(entry, 'summary', '')
                }
                
                if article['link'] and article['title'] != 'No title':
                    articles.append(article)
            
            logger.info(f"بریالیتوب سره {len(articles)} خبرونه واخیستل شول - Successfully fetched {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"د RSS اخیستلو کې تیروتنه: {e} - Error fetching RSS: {e}")
            return []
    
    def translate_to_pashto(self, text):
        """د انګلیسي متن پښتو ته ژباړل - Translate English text to Pashto"""
        try:
            translation = self.translator.translate(text, dest='ps', src='en')
            if translation and translation.text:
                logger.debug(f"ژباړه بریالۍ وه - Translation successful")
                return translation.text
            else:
                return f"[د ژباړې کې ستونزه] {text}"
        except Exception as e:
            logger.error(f"د ژباړې کې تیروتنه: {e} - Translation error: {e}")
            return f"[د ژباړې کې ستونزه] {text}"
    
    def send_telegram_message(self, text):
        """د تلیګرام پیغام لېږل - Send Telegram message"""
        try:
            url = f"{self.telegram_api_url}/sendMessage"
            
            payload = {
                'chat_id': self.channel_username,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('ok'):
                logger.info("پیغام بریالیتوب سره ولېږل شو - Message sent successfully")
                return True
            else:
                logger.error(f"د پیغام لېږلو کې تیروتنه: {result} - Message sending error: {result}")
                return False
                
        except Exception as e:
            logger.error(f"د تلیګرام API کې تیروتنه: {e} - Telegram API error: {e}")
            return False
    
    def generate_detailed_summary(self, article):
        """د تفصیلي تشریح جوړول - Generate detailed summary"""
        try:
            # د اصلي مواد اخیستل - Get original content
            summary = article.get('summary', '')
            title = article.get('title', '')
            
            # د HTML tags پاکول - Remove HTML tags
            if summary:
                clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
            else:
                clean_summary = title
            
            # د OpenAI سره د تفصیلي تشریح جوړول - Generate detailed summary with OpenAI
            if self.openai_client and clean_summary:
                try:
                    prompt = f"""Create a detailed and comprehensive summary of this cryptocurrency news article in English. Make it informative and engaging (2-3 sentences), focusing on key developments, market impact, and significance to the crypto ecosystem.

Title: {title}
Content: {clean_summary}

Requirements:
- Write in clear, professional English
- Focus on facts and impact
- 2-3 sentences maximum
- No promotional language
- Include specific details when available

Provide only the summary text without any formatting or labels."""

                    response = self.openai_client.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a professional cryptocurrency news analyst. Create detailed, factual summaries of crypto news articles that highlight key information and market significance."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=150,
                        temperature=0.7
                    )
                    
                    ai_summary = response.choices[0].message.content.strip()
                    logger.info(f"د AI سره تفصیلي تشریح جوړ شو - Detailed AI summary generated")
                    return ai_summary
                    
                except Exception as e:
                    logger.error(f"د AI کې تیروتنه: {e} - AI error, using fallback")
            
            # د fallback په توګه د RSS content کارول - Use RSS content as fallback
            if clean_summary and len(clean_summary) > 20:
                # د لومړیو ۳ جملو اخیستل - Get first 3 sentences for better summary
                sentences = clean_summary.split('.')
                if len(sentences) > 3:
                    enhanced_summary = '. '.join(sentences[:3]) + '.'
                else:
                    enhanced_summary = clean_summary
                return enhanced_summary
            else:
                return title if title else "No content available"
            
        except Exception as e:
            logger.error(f"د تشریح جوړولو کې تیروتنه: {e} - Summary generation error: {e}")
            return article.get('title', 'No content available')

    def format_news_message(self, article):
        """د خبر د پیغام تشکیل - Format news message"""
        # د تفصیلي تشریح جوړول - Generate detailed summary
        detailed_summary_en = self.generate_detailed_summary(article)
        
        # د تشریح پښتو ته ژباړل - Translate summary to Pashto
        summary_ps = self.translate_to_pashto(detailed_summary_en)
        
        # د پیغام تشکیل یوازې د تفصیلي تشریح سره - Format message with detailed summary only
        message = f"""📖 {detailed_summary_en}
📗 {summary_ps}"""
        
        return message
    
    def is_article_posted(self, article_id):
        """د خبر د لېږل شوي وضعیت کتنه - Check if article was posted"""
        return article_id in self.posted_articles
    
    def mark_article_as_posted(self, article):
        """د خبر د لېږل شوي په توګه ثبتول - Mark article as posted"""
        article_id = article.get('id') or article.get('link')
        
        self.posted_articles[article_id] = {
            'title': article.get('title'),
            'link': article.get('link'),
            'posted_at': datetime.now().isoformat()
        }
        
        self.save_posted_articles()
    
    def process_and_post_article(self, article):
        """د خبر پروسس کول او لېږل - Process and post article"""
        try:
            message = self.format_news_message(article)
            
            if self.send_telegram_message(message):
                self.mark_article_as_posted(article)
                title_preview = article.get('title', '')[:50]
                logger.info(f"خبر بریالیتوب سره ولېږل شو - Article posted successfully: {title_preview}...")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"د خبر پروسس کولو کې تیروتنه: {e} - Error processing article: {e}")
            return False
    
    def check_and_post_new_articles(self):
        """د نویو خبرونو کتنه او لېږل - Check and post new articles"""
        try:
            logger.info("د نویو کریپټو خبرونو کتنه - Checking for new crypto articles")
            
            articles = self.fetch_rss_news()
            if not articles:
                logger.warning("د RSS څخه خبرونه و نه موندل شول - No articles found from RSS")
                return
            
            new_articles_count = 0
            
            for article in articles:
                article_id = article.get('id') or article.get('link')
                
                if not self.is_article_posted(article_id):
                    if self.process_and_post_article(article):
                        new_articles_count += 1
                        time.sleep(2)  # د نرخ محدودیت څخه مخنیوی - Rate limit prevention
                else:
                    logger.debug(f"خبر دمخه لېږل شوی - Article already posted")
            
            if new_articles_count > 0:
                logger.info(f"{new_articles_count} نوي خبرونه ولېږل شول - {new_articles_count} new articles posted")
            else:
                logger.info("د لېږلو لپاره نوي خبرونه نشته - No new articles to post")
                
        except Exception as e:
            logger.error(f"د خبرونو کتنې کې تیروتنه: {e} - Error checking articles: {e}")
    
    def run_periodic_checks(self):
        """د منظمو کتنو اجرا - Run periodic checks"""
        logger.info("د منظمو کتنو پروسه پیل شوه - Periodic checks started")
        
        while self.running:
            try:
                self.check_and_post_new_articles()
                
                # د هرو ۲۴ ساعتونو پاکول - Daily cleanup
                if not hasattr(self, 'last_cleanup') or (datetime.now() - self.last_cleanup).total_seconds() > 86400:
                    self.cleanup_old_entries()
                    self.last_cleanup = datetime.now()
                
                # د ۱۰ دقیقو انتظار - Wait 10 minutes
                logger.info("د راتلونکې کتنې لپاره ۱۰ دقیقې انتظار - Waiting 10 minutes for next check")
                time.sleep(600)
                
            except KeyboardInterrupt:
                logger.info("د کیبورډ څخه ودرولو غوښتنه - Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"د منظمې کتنې کې تیروتنه: {e} - Error in periodic check: {e}")
                time.sleep(60)
    
    def start(self):
        """د بوټ پیل کول - Start bot"""
        if not self.validate_config():
            logger.error("د بوټ تنظیمات سم نه دي - Bot configuration invalid")
            return False
        
        logger.info("🚀 د کریپټو خبرونو بوټ پیل کیږي - Starting crypto news bot")
        
        self.running = True
        
        # د لومړۍ کتنې ترسره کول - Initial check
        self.check_and_post_new_articles()
        
        # د زړو ثبتونو پاکول - Cleanup old entries
        self.cleanup_old_entries()
        self.last_cleanup = datetime.now()
        
        # د منظمو کتنو پیل - Start periodic checks
        self.run_periodic_checks()
        
        return True
    
    def stop(self):
        """د بوټ ودرول - Stop bot"""
        logger.info("د کریپټو خبرونو بوټ ودریږي - Stopping crypto news bot")
        self.running = False
    
    def get_stats(self):
        """د بوټ احصایې - Bot statistics"""
        return {
            'total_posted_articles': len(self.posted_articles),
            'bot_running': self.running,
            'rss_url': self.rss_url,
            'channel': self.channel_username,
            'storage_file': self.storage_file
        }

# د Flask د UptimeRobot لپاره routes - Flask routes for UptimeRobot
@app.route('/')
def home():
    """د کور پاڼه - د UptimeRobot لپاره - Home page for UptimeRobot"""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ps">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>د کریپټو خبرونو بوټ - Crypto News Bot</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            .status {
                background: linear-gradient(45deg, #27ae60, #2ecc71);
                color: white;
                padding: 20px;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
                box-shadow: 0 5px 15px rgba(39, 174, 96, 0.4);
            }
            .emoji {
                font-size: 64px;
                margin: 20px 0;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            .info {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 5px solid #3498db;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 5px;
            }
            .footer {
                margin-top: 30px;
                color: #7f8c8d;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖</div>
            <h1>د کریپټو خبرونو بوټ</h1>
            <h2>Crypto News Bot</h2>
            
            <div class="status">
                ✅ Bot is Running!
            </div>
            
            <div class="info">
                <h3>🔄 د بوټ فعالیت - Bot Activity</h3>
                <p>📡 د کریپټو خبرونو نظارت فعال دی</p>
                <p>🌐 د UptimeRobot لپاره چمتو دی</p>
                <p>⏰ د هرو ۱۰ دقیقو کتنه</p>
                <p>🔗 Monitoring crypto news every 10 minutes</p>
            </div>
            
            <div class="info">
                <h3>📋 د پیغام بڼه - Message Format</h3>
                <div style="background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; text-align: left;">
                    📰 English Title<br>
                    📘 د پښتو سرلیک<br>
                    🔗 https://link.com
                </div>
            </div>
            
            <div class="footer">
                <p>🌐 UptimeRobot Ready | د {{ current_time }} تازه شوی</p>
                <p>Last updated: {{ current_time }} UTC</p>
            </div>
        </div>
    </body>
    </html>
    ''', current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health():
    """د روغتیا کتنې endpoint - Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'د کریپټو خبرونو بوټ فعال دی - Crypto News Bot is active',
        'timestamp': datetime.now().isoformat(),
        'service': 'crypto-news-bot',
        'uptime_ready': True
    })

@app.route('/ping')
def ping():
    """د UptimeRobot لپاره ساده ping - Simple ping for UptimeRobot"""
    return jsonify({
        'status': 'alive',
        'message': 'Bot is running!',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stats')
def stats():
    """د بوټ احصایې - Bot statistics"""
    try:
        if 'bot_instance' in globals():
            return jsonify(bot_instance.get_stats())
        else:
            return jsonify({
                'status': 'initializing',
                'message': 'Bot is starting up'
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        })

def run_flask_server():
    """د Flask سرور اجرا - Run Flask server"""
    try:
        logger.info("🌐 د UptimeRobot لپاره Flask سرور پیل کول - Starting Flask server for UptimeRobot")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"د Flask سرور کې تیروتنه: {e} - Flask server error: {e}")

def run_crypto_bot():
    """د کریپټو بوټ اجرا - Run crypto bot"""
    global bot_instance
    try:
        bot_instance = CryptoNewsBot()
        bot_instance.start()
    except Exception as e:
        logger.error(f"د بوټ کې تیروتنه: {e} - Bot error: {e}")
        time.sleep(60)
        run_crypto_bot()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 د کریپټو خبرونو تلیګرام بوټ پیل کول - Starting Telegram Crypto News Bot")
    logger.info("📍 د UptimeRobot سره د 24/7 فعالیت لپاره - For 24/7 activity with UptimeRobot")
    logger.info("=" * 60)
    
    # د Flask سرور په شالید کې پیل کول - Start Flask server in background
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask سرور د UptimeRobot لپاره پیل شو - Flask server started for UptimeRobot")
    
    # د کریپټو بوټ په اصلي thread کې پیل کول - Start crypto bot in main thread
    run_crypto_bot()