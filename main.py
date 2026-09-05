import os
import re
import urllib.parse
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
HF_TOKEN = os.environ.get("HF_TOKEN")

# မြန်မာဘာသာစကားနှင့် ကလေးများအတွက် သင်တော်သော Model
TEXT_MODEL = "Qwen/Qwen2.5-72B-Instruct"

# ကလေးများအတွက် ဖော်ရွေသော Prompt စနစ်
SYSTEM_PROMPT = (
    "You are a friendly, kind, and smart AI assistant for kids and learners. "
    "Always speak in clean, highly natural, polite, and grammatically correct Myanmar language (Burmese). "
    "Encourage creativity, fun learning, and curiosity. Keep your answers easy to understand for children."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "မင်္ဂလာပါကွယ်... 🌟\n"
        "ဦးဦး ကလေးတို့ရဲ့ AI စက်ရုပ်ငယ်လေးပါပဲ။\n\n"
        "✨ စာအုပ်ထဲက သိချင်တာတွေ မေးလို့ရတယ်\n"
        "🎨 'ပုံဆွဲပေးပါ' ဆိုရင် ပုံလှလှလေးတွေ ဆွဲပေးမယ်\n"
        "🧩 ပဟေဠိနဲ့ စိတ်ကူးယဉ် ပုံပြင်တွေလည်း ပြောပြပေးမယ်နော်!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # ၁။ ပုံဆွဲခိုင်းကြောင်း စစ်ဆေးခြင်း (Image Request)
    image_keywords = ["ပုံဆွဲ", "ပုံဆွဲပေး", "ပုံပြပါ", "draw", "image", "picture", "photo"]
    is_image_request = any(keyword in user_text.lower() for keyword in image_keywords)
    
    if is_image_request:
        await update.message.reply_text("ခဏလေးစောင့်နော်... ဦးဦး ပုံလှလှလေး ဆွဲပေးနေပါတယ်။ 🎨✨")
        try:
            # မြန်မာလိုပြောထားသည်များကို English Prompt သို့ ပြောင်းလဲခြင်း
            client = InferenceClient(model=TEXT_MODEL, token=HF_TOKEN, timeout=20)
            translate_prompt = [
                {"role": "system", "content": "Translate the user's image request into a detailed image generation prompt in English. Output only the English prompt."},
                {"role": "user", "content": user_text}
            ]
            trans_res = client.chat_completion(messages=translate_prompt, max_tokens=100)
            english_prompt = trans_res.choices[0].message.content.strip()
            
            # Pollinations.ai အခမဲ့ Image Generator ကို သုံး၍ ပုံထုတ်ခြင်း
            encoded_prompt = urllib.parse.quote(english_prompt)
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed=42"
            
            await update.message.reply_photo(photo=image_url, caption=f"🖼️ ကလေးလေး တောင်းဆိုထားတဲ့ ပုံလေး ရပါပြီရှင်!\n\n*(Prompt: {english_prompt})*")
            return
        except Exception as e:
            await update.message.reply_text("ပုံဆွဲရာတွင် အခက်အခဲရှိသွားပါသည်၊ နောက်တစ်ကြိမ် ပြန်စမ်းကြည့်ပေးပါနော်။")
            return

    # ၂။ စကားပြောဆိုခြင်းနှင့် စာမေးခြင်း (Text Chat Response)
    try:
        client = InferenceClient(model=TEXT_MODEL, token=HF_TOKEN, timeout=30)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
        
        response = client.chat_completion(
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
        
    except Exception as e:
        await update.message.reply_text("ဦးဦး စဉ်းစားရတာ ခဏလေး လိုင်းထွေးသွားလို့ပါ၊ နောက်တစ်ခေါက် ပြန်မေးကြည့်ပေးပါဦးနော်။")

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling(drop_pending_updates=True)
