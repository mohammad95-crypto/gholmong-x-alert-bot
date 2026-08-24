from flask import Flask
import threading
import os

from x_monitor import monitor_accounts

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)


app = Flask(__name__)


@app.route("/")
def home():
    return "GHOLMONG X Alert Bot is running!"


# ذخیره موقت اکانت‌ها
watch_list = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👾 GHOLMONG X Alert Bot\n\n"
        "Commands:\n"
        "/add username\n"
        "/list"
    )


async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        await update.message.reply_text(
            "Use:\n/add username"
        )
        return

    username = context.args[0].replace("@", "")

    if username not in watch_list:
        watch_list.append(username)

    await update.message.reply_text(
        f"✅ Added @{username}"
    )


async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not watch_list:
        await update.message.reply_text(
            "No accounts added."
        )
        return

    text = "👀 Watching:\n\n"

    for user in watch_list:
        text += f"• @{user}\n"

    await update.message.reply_text(text)


# دریافت پست جدید X
def send_alert(post):

    print("🚨 NEW X POST")
    print(f"Account: @{post['username']}")
    print(f"Text: {post['text']}")
    print(f"Link: {post['link']}")


def run_flask():

    app.run(
        host="0.0.0.0",
        port=10000
    )


def run_bot():

    token = os.getenv("BOT_TOKEN")

    application = Application.builder()\
        .token(token)\
        .build()


    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("add", add_account)
    )

    application.add_handler(
        CommandHandler("list", list_accounts)
    )


    print("GHOLMONG Telegram Bot Started")

    application.run_polling()



if __name__ == "__main__":

    threading.Thread(
        target=run_flask
    ).start()


    threading.Thread(
        target=monitor_accounts,
        args=(watch_list, send_alert),
        daemon=True
    ).start()


    run_bot()
