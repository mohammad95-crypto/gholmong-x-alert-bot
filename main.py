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

app = Flask(**name**)

@app.route("/")
def home():
return "GHOLMONG X Alert Bot is running!"

DATABASE_URL = os.getenv("DATABASE_URL")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")

telegram_app = None
telegram_loop = None

def db_connect():
return psycopg2.connect(DATABASE_URL)

def init_db():

```
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
```

def is_owner(update: Update):

```
if not OWNER_CHAT_ID:
    return False

if not update.effective_chat:
    return False

return str(update.effective_chat.id) == str(OWNER_CHAT_ID)
```

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
if not is_owner(update):
    return

await update.message.reply_text(
    "👾 GHOLMONG X Alert Bot\n\n"
    "/add username\n"
    "/list"
)
```

async def add_account(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
if not is_owner(update):
    return

if not context.args:
    await update.message.reply_text(
        "Use:\n/add username"
    )
    return

username = context.args[0].replace("@", "").strip()

if not username:
    await update.message.reply_text(
        "Invalid username."
    )
    return

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
```

async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
if not is_owner(update):
    return

conn = db_connect()
cur = conn.cursor()

cur.execute(
    "SELECT username FROM accounts ORDER BY id"
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
```

async def send_telegram_alert(post):

```
if not OWNER_CHAT_ID:
    print("OWNER_CHAT_ID is not configured.")
    return

if telegram_app is None:
    print("Telegram application is not ready.")
    return

message = (
    "🚨 NEW X POST\n\n"
    f"👤 @{post['username']}\n\n"
    f"{post['text']}\n\n"
    f"🔗 {post['link']}"
)

try:
    await telegram_app.bot.send_message(
        chat_id=int(OWNER_CHAT_ID),
        text=message
    )

    print(
        f"✅ Alert sent to owner for @{post['username']}"
    )

except Exception as e:
    print(f"❌ Failed to send Telegram alert: {e}")
```

def send_alert(post):

```
global telegram_loop

if telegram_loop is None:
    print("Telegram event loop is not ready.")
    return

try:
    future = asyncio.run_coroutine_threadsafe(
        send_telegram_alert(post),
        telegram_loop
    )

    future.result(timeout=30)

except Exception as e:
    print(f"❌ Alert error: {e}")
```

def run_flask():

```
app.run(
    host="0.0.0.0",
    port=10000
)
```

def run_bot():

```
global telegram_app
global telegram_loop

token = os.getenv("BOT_TOKEN")

if not token:
    print("BOT_TOKEN is not configured.")
    return

telegram_app = (
    Application.builder()
    .token(token)
    .build()
)

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

telegram_loop = asyncio.new_event_loop()
asyncio.set_event_loop(telegram_loop)

telegram_loop.run_until_complete(
    telegram_app.initialize()
)

telegram_loop.run_until_complete(
    telegram_app.start()
)

telegram_loop.run_until_complete(
    telegram_app.updater.start_polling()
)

telegram_loop.run_forever()
```

if **name** == "**main**":

```
init_db()

threading.Thread(
    target=run_flask,
    daemon=True
).start()

threading.Thread(
    target=monitor_accounts,
    args=(send_alert,),
    daemon=True
).start()

run_bot()
```

