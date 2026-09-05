import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Render Web Port အတွက် Fake Web Server
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Setup
genai.configure(api_key=GEMINI_API_KEY)

# Gemini 1.5/2.5 Model ကို စနစ်တကျ ခေါ်ယူခြင်း
model = genai.GenerativeModel('models/gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အမြဲတမ်း နိုးကြားနေတဲ့ AI အကူစက်ရုပ်လေးပါ။ ဘာခိုင်းချင်ပါသလဲခင်ဗျာ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        response = model.generate_content(
            f"You are a helpful AI assistant. Reply fluently in Myanmar language.\nUser message: {user_text}"
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        # Fallback လုပ်ဆောင်ချက် - အကယ်၍ models/ Prefix မပါဘဲ စမ်းသပ်ခြင်း
        try:
            fallback_model = genai.GenerativeModel('gemini-1.5-flash')
            res = fallback_model.generate_content(user_text)
            await update.message.reply_text(res.text)
        except Exception as err:
            await update.message.reply_text(f"Error တက်သွားပါသည်: {str(e)}")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()
