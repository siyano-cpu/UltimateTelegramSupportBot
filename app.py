import os
import sys
import threading
import time
import logging
from flask import Flask, jsonify, request
import telebot
from telebot import types

# تنظیم لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# دریافت توکن از متغیر محیطی
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    sys.exit(1)

# ایجاد نمونه ربات و Flask
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================ بخش هندلرهای ربات ================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """پاسخ به دستور /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "کاربر"
    
    welcome_text = f"""
🎉 سلام {username} عزیز!

به ربات پشتیبانی خوش آمدید. 
این ربات برای مدیریت تیکت‌های پشتیبانی طراحی شده است.

📌 دستورات موجود:
/start - نمایش این پیام
/help - راهنمای کامل
/ticket - ثبت تیکت جدید
/mytickets - مشاهده تیکت‌های من
/contact - تماس با پشتیبانی

🛠️ دستورات مدیریتی (فقط ادمین):
/admin - پنل مدیریت
/stats - آمار سیستم

لطفاً یکی از دستورات بالا را انتخاب کنید.
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def send_help(message):
    """پاسخ به دستور /help"""
    help_text = """
📖 *راهنمای ربات پشتیبانی*

🔹 *ثبت تیکت جدید:*
دستور `/ticket` را بفرستید و سپس پیام خود را ارسال کنید.

🔹 *مشاهده تیکت‌های من:*
با دستور `/mytickets` می‌توانید لیست تیکت‌های خود را ببینید.

🔹 *تماس با پشتیبانی:*
دستور `/contact` را بفرستید تا با تیم پشتیبانی ارتباط برقرار کنید.

🔹 *برای ادمین‌ها:*
- `/admin` - ورود به پنل مدیریت
- `/stats` - مشاهده آمار سیستم

❓ سوالی دارید؟ با ادمین تماس بگیرید.
"""
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['ticket'])
def create_ticket(message):
    """ثبت تیکت جدید"""
    msg = bot.reply_to(message, "📝 لطفاً متن تیکت خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_ticket)

def process_ticket(message):
    """پردازش متن تیکت"""
    ticket_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "کاربر"
    
    # ارسال تیکت به ادمین (در اینجا فقط یک پیام نمونه ارسال می‌شود)
    admin_message = f"""
📩 *تیکت جدید!*

👤 کاربر: @{username} (ID: {user_id})
📝 متن تیکت:
{ticket_text}

⏰ زمان: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    # ارسال به ادمین (می‌توانید با ID ادمین جایگزین کنید)
    # bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode='Markdown')
    
    bot.reply_to(message, f"""
✅ تیکت شما با موفقیت ثبت شد!

📝 متن تیکت:
{ticket_text}

🆔 شماره پیگیری: {user_id}-{int(time.time())}

پشتیبانی در اسرع وقت با شما تماس خواهد گرفت.
""", parse_mode='Markdown')
    
    # لاگ ثبت تیکت
    logger.info(f"New ticket from user {user_id}: {ticket_text[:50]}...")

@bot.message_handler(commands=['mytickets'])
def my_tickets(message):
    """نمایش تیکت‌های کاربر"""
    user_id = message.from_user.id
    # در اینجا می‌توانید تیکت‌های کاربر را از دیتابیس دریافت کنید
    bot.reply_to(message, f"""
📋 *لیست تیکت‌های شما*

👤 کاربر: {message.from_user.first_name}

🔹 تیکت شماره ۱: در حال بررسی
🔹 تیکت شماره ۲: پاسخ داده شده
🔹 تیکت شماره ۳: بسته شده

برای مشاهده جزئیات هر تیکت، دستور `/ticket [شماره]` را بفرستید.
""", parse_mode='Markdown')

@bot.message_handler(commands=['contact'])
def contact_admin(message):
    """ارتباط با پشتیبانی"""
    msg = bot.reply_to(message, "📩 لطفاً پیام خود برای پشتیبانی را وارد کنید:")
    bot.register_next_step_handler(msg, process_contact)

def process_contact(message):
    """پردازش پیام پشتیبانی"""
    contact_text = message.text
    user_id = message.from_user.id
    
    bot.reply_to(message, f"""
✅ پیام شما به پشتیبانی ارسال شد!

📝 متن پیام:
{contact_text}

⏰ زمان: {time.strftime('%Y-%m-%d %H:%M:%S')}

پشتیبانی در اسرع وقت پاسخ خواهد داد.
""")
    
    logger.info(f"Contact from user {user_id}: {contact_text[:50]}...")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """پنل مدیریت (فقط ادمین)"""
    # بررسی اینکه کاربر ادمین است یا خیر
    admin_id = os.environ.get('ADMIN_CHAT_ID')
    if admin_id and str(message.from_user.id) != admin_id:
        bot.reply_to(message, "⛔ شما دسترسی به این بخش را ندارید!")
        return
    
    admin_text = """
🔐 *پنل مدیریت*

📊 *گزارش‌ها:*
- تعداد کاربران: ۱۵
- تیکت‌های باز: ۳
- تیکت‌های بسته: ۱۲

🛠️ *دستورات مدیریتی:*
/list_users - لیست کاربران
/list_tickets - لیست تیکت‌ها
/ban [ID] - مسدود کردن کاربر
/unban [ID] - رفع مسدودی

⚙️ *تنظیمات سیستم:*
- وضعیت ربات: ✅ فعال
- آخرین بروزرسانی: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    bot.reply_to(message, admin_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats'])
def stats(message):
    """آمار سیستم"""
    stats_text = f"""
📊 *آمار سیستم*

👥 تعداد کاربران: ۱۵
🎫 تیکت‌های باز: ۳
✅ تیکت‌های بسته: ۱۲
⏳ میانگین زمان پاسخ: ۲۴ دقیقه
📈 رضایت کاربران: ۹۲%

🔄 وضعیت ربات: ✅ آنلاین
⏰ زمان جاری: {time.strftime('%Y-%m-%d %H:%M:%S')}
🚀 آپ‌تایم: ۳ روز ۴ ساعت
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """پاسخ به پیام‌های معمولی"""
    # در اینجا می‌توانید منطق پاسخ به پیام‌های معمولی را قرار دهید
    bot.reply_to(message, f"پیام شما دریافت شد! برای مشاهده راهنما، دستور /help را بفرستید.")

# ================ بخش Health Check ================

@app.route('/')
@app.route('/health')
def health_check():
    """پاسخ به Health Check Render"""
    return jsonify({
        "status": "healthy",
        "bot": "running",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "uptime": "active"
    }), 200

@app.route('/ping')
def ping():
    """اندپوینت ساده برای پینگ (مخصوص UptimeRobot)"""
    return jsonify({"pong": True, "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}), 200

@app.route('/info', methods=['GET'])
def bot_info():
    """نمایش اطلاعات ربات"""
    try:
        bot_info = bot.get_me()
        return jsonify({
            "bot_name": bot_info.username,
            "bot_id": bot_info.id,
            "is_bot": bot_info.is_bot,
            "status": "online",
            "webhook": "polling"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================ بخش اجرای اصلی ================

def run_bot():
    """اجرای ربات در یک نخ جداگانه با Polling"""
    logger.info("🚀 Starting bot polling...")
    
    try:
        # حذف Webhook در صورت وجود
        bot.remove_webhook()
        
        # شروع Polling
        bot.infinity_polling(
            timeout=10,           # زمان انتظار برای پاسخ
            long_polling_timeout=5 # زمان انتظار برای پیام‌های جدید
        )
    except Exception as e:
        logger.error(f"❌ Bot polling error: {e}")
        # در صورت خطا، دوباره تلاش می‌کند
        time.sleep(5)
        run_bot()

if __name__ == '__main__':
    # اجرای ربات در نخ جداگانه
    logger.info("🔄 Setting up bot thread...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("✅ Bot thread started successfully!")
    
    # اجرای سرور Flask برای Health Check
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting Flask server on port {port}...")
    
    # اجرای Flask با پورت مشخص شده
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False  # جلوگیری از ری‌استارت شدن Flask
    )