import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from groq import Groq

# =========================
# API Keys
# =========================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN မတွေ့ပါ။")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY မတွေ့ပါ။")

# =========================
# Groq Client
# =========================
client = Groq(api_key=GROQ_API_KEY)

MODEL = "llama-3.3-70b-versatile"


# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "မင်္ဂလာပါ! 🤖\n"
        "သားသားရဲ့ AI အကူစက်ရုပ်လေးပါ။\n"
        "ဘာခိုင်းချင်ပါသလဲခင်ဗျာ?"
    )


# =========================
# Handle Messages
# =========================
async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    try:
        # Groq API
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful and smart AI assistant. "
                        "You understand Myanmar language very well. "
                        "Always reply naturally and clearly in Myanmar "
                        "language when the user speaks Myanmar."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text,
                },
            ],
        )

        reply_text = response.choices[0].message.content

        if not reply_text:
            reply_text = "တောင်းပန်ပါတယ်။ အဖြေမရရှိသေးပါ။"

        await update.message.reply_text(reply_text)

    except Exception as e:
        print("Groq Error:", repr(e))

        await update.message.reply_text(
            "တောင်းပန်ပါတယ်ခင်ဗျာ 😥\n"
            "AI server ဘက်မှာ ခဏအခက်အခဲရှိနေပါတယ်။"
        )


# =========================
# Main
# =========================
def main():

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
