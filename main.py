from flask import Flask
import threading
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

@app.route("/")
def home():
    return "GHOLMONG X Alert Bot is running!"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 GHOLMONG Alert Bot is alive!"
    )


def run_flask():
    app.run(host="0.0.0.0", port=10000)


def run_bot():
    token = os.getenv("BOT_TOKEN")

    if not token:
        print("BOT_TOKEN missing!")
        return

    application = Application.builder().token(token).build()

    application.add_handler(
        CommandHandler("start", start)
    )

    print("Telegram Bot Started!")

    application.run_polling()


if __name__ == "__main__":

    threading.Thread(
        target=run_flask
    ).start()

    run_bot()
