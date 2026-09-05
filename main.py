import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# Render Keep-Alive Server
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
HF_TOKEN = os.environ.get("HF_TOKEN") # Render အဝန်းအဝိုင်းမှ HF_TOKEN ကို ဖတ်ယူခြင်း

# Models စာရင်း
MODELS = [
    "Qwen/Qwen2.5-Coder-32B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အမြဲတမ်း နိုးကြားနေတဲ့ AI အကူစက်ရုပ်လေးပါ။ ဘာခိုင်းချင်ပါသလဲခင်ဗျာ?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Always respond fluently in Myanmar language."},
        {"role": "user", "content": user_text}
    ]
    
    # Model များကို တစ်ခုပြီးတစ်ခု စမ်းသပ်မည့် ပတ်လမ်း
    for model_name in MODELS:
        try:
            client = InferenceClient(model=model_name, token=HF_TOKEN, timeout=30)
            response = client.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            await update.message.reply_text(reply)
            return  # အောင်မြင်ပါက ပတ်လမ်းကို ရပ်မည်
        except Exception:
            continue  # အဆင်မပြေပါက နောက်တစ်မျိုးသို့ ပြောင်းမည်
            
    await update.message.reply_text("ခဏမျှ တောင်းပန်ပါသည်၊ Server မျာ ခေတ္တ အလုပ်ရှုပ်နေပါသဖြင့် နောက်မှ ပြန်စမ်းကြည့်ပေးပါ။")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling(drop_pending_updates=True)
