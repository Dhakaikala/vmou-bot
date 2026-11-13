import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from flask import Flask
from threading import Thread

# Flask Web Server (Render ke liye taaki bot 24/7 active rahe)
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "VMOU Bot is active and running 24/7! 🚀"

def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# VMOU Database (Apne file_ids yahan update karein)
VMOU_DATABASE = {
    "blis": {
        "title": "📚 BLIS (Library Science)",
        "subjects": {
            "blis_01": {"name": "BLIS-01: Library & Society", "file_id": "YOUR_FILE_ID_FOR_BLIS_01"},
            "blis_02": {"name": "BLIS-02: Library Classification", "file_id": "YOUR_FILE_ID_FOR_BLIS_02"}
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_text = f"Namaste **{user_name}** ji! 🙏\n\nVMOU Bot me aapka swagat hai. Apna course select karein ya subject code bhejein (jaise: `blis_01`)."

    keyboard = [
        [InlineKeyboardButton("📚 BLIS (Library Science)", callback_data="cat_blis")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help_info")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cat_blis":
        subjects = VMOU_DATABASE["blis"]["subjects"]
        keyboard = [[InlineKeyboardButton(sub["name"], callback_data=f"sub_{code}")] for code, sub in subjects.items()]
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text("📚 **BLIS Subjects:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "main_menu":
        await query.edit_message_text("🙏 **VMOU Bot Menu**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 BLIS", callback_data="cat_blis")]]))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        doc = update.message.document
        await update.message.reply_text(f"📁 File ID:\n`{doc.file_id}`", parse_mode="Markdown")
        return

    text = update.message.text.strip().lower().replace("-", "_")
    for cat in VMOU_DATABASE.values():
        if text in cat["subjects"]:
            sub = cat["subjects"][text]
            await update.message.reply_document(document=sub["file_id"], caption=f"📄 {sub['name']}")
            return
    await update.message.reply_text("⚠️ Sahi subject code enter karein (jaise: `blis_01`).")

def main():
    # Render Environment Variable se Token uthayega
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    # Flask ko background me chalu karein
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_messages))

    print("🚀 Telegram Bot Polling Started...")
    app.run_polling()

if __name__ == '__main__':
    main()
  
