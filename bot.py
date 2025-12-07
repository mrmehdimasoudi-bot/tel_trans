import logging
import os
from threading import Thread
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from deep_translator import GoogleTranslator

# =======================================================
# تنظیمات ربات
# =======================================================
TOKEN = "8406136784:AAG_UOW5tYFkKjXy7OuawNVK1PFeeatHomw" 
SOURCE_CHANNEL_ID = -1003418452759  
TARGET_CHANNEL_ID = "@manika_es"    
# =======================================================

# --- بخش 1: سرور ساختگی وب (برای راضی نگه داشتن Render) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_http():
    # رندر پورت را در متغیر محیطی PORT می‌فرستد
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_http)
    t.start()
# ---------------------------------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def handle_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.channel_post
    if not msg or update.effective_chat.id != SOURCE_CHANNEL_ID:
        return

    print(f"📩 ID={msg.message_id}")

    photo_file_id = msg.photo[-1].file_id if msg.photo else None
    original_text = msg.caption if photo_file_id else msg.text
    final_text = ""

    if original_text:
        try:
            translator = GoogleTranslator(source='fa', target='es')
            final_text = translator.translate(original_text)
        except Exception:
            final_text = f"{original_text} \n(Error translation)"
    
    try:
        chat_id = TARGET_CHANNEL_ID
        if photo_file_id:
            if len(final_text) > 1000:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file_id, caption="Ver abajo 👇")
                await context.bot.send_message(chat_id=chat_id, text=final_text)
            else:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file_id, caption=final_text)
        elif final_text:
             await context.bot.send_message(chat_id=chat_id, text=final_text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # اجرای سرور وب در پس‌زمینه
    keep_alive()
    
    # اجرای ربات
    application = ApplicationBuilder().token(TOKEN).build()
    channel_filter = filters.Chat(chat_id=SOURCE_CHANNEL_ID)
    handler = MessageHandler(channel_filter, handle_post)
    application.add_handler(handler)
    application.run_polling()