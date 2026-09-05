import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# Render Web Port အတွက် Keep-Alive Server
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

# Token မလိုဘဲ အသုံးပြုနိုင်သော Public Server Endpoint
client = InferenceClient(
    model="Qwen/Qwen2.5-Coder-32B-Instruct",
    timeout=60
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အမြဲတမ်း နိုးကြားနေတဲ့ AI အကူစက်ရုပ်လေးပါ။ ဘာခိုင်းချင်ပါသလဲခင်ဗျာ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        # Free API Key ပါဝင်သော Request
        messages = [
            {"role": "system", "content": "You are a helpful and intelligent AI assistant. Always respond fluently and naturally in Myanmar language."},
            {"role": "user", "content": user_text}
        ]
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        reply_text = response.choices[0].message.content
        await update.message.reply_text(reply_text)
        
    except Exception as e:
        # Fallback - အကယ်၍ Qwen အဆင်မပြေပါက တခြား Free Endpoint သုံးရန်
        try:
            fallback_client = InferenceClient("HuggingFaceH4/zephyr-7b-beta")
            response = fallback_client.chat_completion(
                messages=[{"role": "user", "content": user_text}],
                max_tokens=500
            )
            await update.message.reply_text(response.choices[0].message.content)
        except Exception as err:
            await update.message.reply_text(f"Error တက်သွားပါသည်: {str(err)}")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling(drop_pending_updates=True)
