from flask import Flask
import threading
import os
import psycopg2
import asyncio

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


DATABASE_URL = os.getenv("DATABASE_URL")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")

telegram_app = None


def db_connect():
    return psycopg2.connect(DATABASE_URL)


def init_db():

    conn = db_connect()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE
    )
    """)

    conn.commit()
    cur.close()
    conn.close()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👾 GHOLMONG X Alert Bot\n\n"
        "/add username\n"
        "/list"
    )



async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Use:\n/add username"
        )
        return


    username = context.args[0].replace("@", "")


    conn = db_connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO accounts(username) VALUES(%s) ON CONFLICT DO NOTHING",
        (username,)
    )

    conn.commit()

    cur.close()
    conn.close()


    await update.message.reply_text(
        f"✅ Added @{username}"
    )



async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    conn = db_connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT username FROM accounts"
    )

    accounts = cur.fetchall()

    cur.close()
    conn.close()


    if not accounts:

        await update.message.reply_text(
            "No accounts added."
        )
        return


    text = "👀 Watching:\n\n"

    for account in accounts:
        text += f"• @{account[0]}\n"


    await update.message.reply_text(text)



async def send_telegram_alert(post):

    if not OWNER_CHAT_ID:
        return


    message = (
        "🚨 NEW X POST\n\n"
        f"👤 @{post['username']}\n\n"
        f"{post['text']}\n\n"
        f"🔗 {post['link']}"
    )


    await telegram_app.bot.send_message(
        chat_id=OWNER_CHAT_ID,
        text=message
    )



def send_alert(post):

    if telegram_app:

        asyncio.run(
            send_telegram_alert(post)
        )



def run_flask():

    app.run(
        host="0.0.0.0",
        port=10000
    )



def run_bot():

    global telegram_app


    token = os.getenv("BOT_TOKEN")


    telegram_app = Application.builder()\
        .token(token)\
        .build()



    telegram_app.add_handler(
        CommandHandler("start", start)
    )

    telegram_app.add_handler(
        CommandHandler("add", add_account)
    )

    telegram_app.add_handler(
        CommandHandler("list", list_accounts)
    )


    print("GHOLMONG Telegram Bot Started")


    telegram_app.run_polling()



if __name__ == "__main__":


    init_db()


    threading.Thread(
        target=run_flask
    ).start()


    threading.Thread(
        target=monitor_accounts,
        args=(send_alert,),
        daemon=True
    ).start()


    run_bot()
