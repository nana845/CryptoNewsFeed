"""
Main entry point for the Telegram crypto news bot.
Handles Flask server for Replit keep-alive and starts the bot.
"""

import threading
import time
from flask import Flask, render_template
from bot import CryptoNewsBot
from keep_alive import keep_alive  # د ژوندي ساتلو سیسټم - Keep-alive system
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for keep-alive functionality
app = Flask(__name__)

@app.route('/')
def home():
    """Home page showing bot status"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'message': 'Crypto News Bot is running'}

def run_flask():
    """Run Flask server in a separate thread"""
    try:
        # د اصلي Flask سرور د مختلف پورټ کارول - Use different port for main Flask server
        app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}")

def run_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        bot = CryptoNewsBot()
        bot.start()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        # Restart bot after error
        time.sleep(60)
        run_bot()

if __name__ == "__main__":
    logger.info("Starting Crypto News Bot...")
    
    # د UptimeRobot لپاره د ژوندي ساتلو سیسټم پیل کول - Start keep-alive system for UptimeRobot
    keep_alive()
    
    # Start Flask server in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Start bot in main thread
    run_bot()
