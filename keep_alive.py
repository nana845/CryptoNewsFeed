#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
د بوټ د ژوندي ساتلو سیسټم - UptimeRobot لپاره
Bot Keep-Alive System for UptimeRobot
"""

from flask import Flask
import threading
import logging

# د لاګنګ تنظیمات - Logging setup
logger = logging.getLogger(__name__)

# د Flask اپلیکیشن جوړول - Create Flask application
app = Flask(__name__)

@app.route('/')
def home():
    """د کور پاڼه - د UptimeRobot لپاره اصلي endpoint - Home page - Main endpoint for UptimeRobot"""
    return """
    <!DOCTYPE html>
    <html lang="ps">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crypto Bot - فعال دی</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
            }
            .status {
                color: #27ae60;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }
            .emoji {
                font-size: 48px;
                margin: 20px 0;
            }
            .info {
                color: #7f8c8d;
                margin: 10px 0;
            }
            .uptime-info {
                background: #e8f5e8;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #27ae60;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="emoji">🤖</div>
            <h1>Crypto News Bot</h1>
            <div class="status">✅ Bot is Running!</div>
            
            <div class="uptime-info">
                <h3>د بوټ حالت - Bot Status</h3>
                <p>📡 د کریپټو خبرونو نظارت فعال دی</p>
                <p>🔄 Crypto news monitoring active</p>
                <p>🌐 UptimeRobot ready for monitoring</p>
            </div>
            
            <div class="info">
                <p>د دغه URL د UptimeRobot سره وکاروئ</p>
                <p>Use this URL with UptimeRobot</p>
            </div>
            
            <div class="info">
                <small>د هرو ۱۰ دقیقو په موده کې د نویو خبرونو کتنه</small><br>
                <small>Checking for new articles every 10 minutes</small>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/ping')
def ping():
    """د پنګ endpoint - د UptimeRobot لپاره ساده ځواب - Ping endpoint - Simple response for UptimeRobot"""
    return {
        'status': 'alive',
        'message': 'Bot is running!',
        'service': 'crypto-news-bot'
    }

@app.route('/health')
def health():
    """د روغتیا کتنې endpoint - Health check endpoint"""
    return {
        'status': 'healthy',
        'bot_status': 'running',
        'message': 'د کریپټو خبرونو بوټ فعال دی - Crypto News Bot is active',
        'uptime_ready': True
    }

@app.route('/status')
def status():
    """د بوټ د حالت کتنې endpoint - Bot status check endpoint"""
    return {
        'bot_running': True,
        'monitoring': 'active',
        'rss_source': 'cointelegraph.com',
        'check_interval': '10 minutes',
        'uptime_monitoring': 'ready'
    }

def keep_alive():
    """د بوټ د ژوندي ساتلو اصلي فنکشن - Main keep-alive function"""
    def run():
        """د Flask سرور اجرا کول - Run Flask server"""
        try:
            logger.info("🌐 د ژوندي ساتلو سرور پیل کول په 8080 پورټ - Starting keep-alive server on port 8080")
            # د Replit لپاره 0.0.0.0 host کارول ضروری دي - Using 0.0.0.0 host is required for Replit
            app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
        except Exception as e:
            logger.error(f"د Flask سرور کې تیروتنه: {e} - Flask server error: {e}")
    
    # د Flask سرور په جلا thread کې پیل کول - Start Flask server in separate thread
    flask_thread = threading.Thread(target=run, daemon=True)
    flask_thread.start()
    
    logger.info("✅ د ژوندي ساتلو سیسټم فعال شو - Keep-alive system activated")
    logger.info("🔗 UptimeRobot URL: https://your-repl-name.replit.app")
    logger.info("📍 د نظارت لپاره دا URL د UptimeRobot سره وکاروئ - Use this URL with UptimeRobot for monitoring")

if __name__ == "__main__":
    # د ازمویلو لپاره مستقل اجرا - Independent run for testing
    keep_alive()
    
    # د بې پایه لوپ ساتل تر څو سرور فعال پاتې شي - Keep infinite loop to keep server running
    try:
        while True:
            import time
            time.sleep(60)
            logger.info("⏰ د ژوندي ساتلو سیسټم فعال دی - Keep-alive system is active")
    except KeyboardInterrupt:
        logger.info("🛑 د ژوندي ساتلو سیسټم ودرول شو - Keep-alive system stopped")