import os
import sys
import threading
import time
import logging
from flask import Flask, jsonify
import telebot

# تنظیم لاگ‌گیری
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# دریافت توکن
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ===== هندلرهای ربات (همان کدهای اصلی) =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات پشتیبانی خوش آمدید.")

# بقیه هندلرهای خود را اینجا اضافه کنید...

# ===== Health Check =====
@app.route('/')
@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "running"}), 200

def run_bot():
    """اجرای ربات در نخ جداگانه"""
    logger.info("Starting bot polling...")
    try:
        bot.remove_webhook()
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        time.sleep(5)

if __name__ == '__main__':
    # اجرای ربات در نخ جداگانه
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # اجرای سرور Flask
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
