import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# 1. Key များကို ရယူခြင်း
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Groq AI ချိတ်ဆက်ခြင်း
client = Groq(api_key=GROQ_API_KEY)

# /start လို့ စာပို့ရင် ပြန်ဖြေမည့် Function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("မင်္ဂလာပါ! အမြဲတမ်း နိုးကြားနေတဲ့ သားသားရဲ့ AI အကူစက်ရုပ်လေးပါ။ ဘာခိုင်းချင်ပါသလဲခင်ဗျာ?")

# စာများ ပို့လာပါက AI က စဉ်းစားပြီး ပြန်ဖြေပေးမည့် Function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # AI ထံ မေးခွန်းပို့ပြီး မြန်မာလို အစွမ်းကုန် စဉ်းစားခိုင်းခြင်း
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # သို့မဟုတ် deepseek-r1-distill-llama-70b
        messages=[
            {"role": "system", "content": "You are a helpful and smart AI assistant who understands and replies fluently in Myanmar language."},
            {"role": "user", "content": user_text}
        ]
    )
    
    reply_text = response.choices[0].message.content
    await update.message.reply_text(reply_text)

if __name__ == '__main__':
    # Telegram Bot စတင်ခြင်း
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running 24/7...")
    app.run_polling()
