```python
import feedparser
import time
import os
import psycopg2


checked_posts = {}


def db_connect():
    return psycopg2.connect(
        os.getenv("DATABASE_URL")
    )


def get_accounts():

    conn = db_connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT username FROM accounts ORDER BY id"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]


def check_account(username):

    url = f"https://nitter.net/{username}/rss"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"❌ Error checking @{username}: {e}")
        return None

    if not feed.entries:
        return None

    latest = feed.entries[0]

    post_id = latest.get("id")

    if not post_id:
        return None

    # اولین بررسی فقط آخرین پست را ثبت می‌کند
    # و برای آن Alert ارسال نمی‌شود.
    if username not in checked_posts:

        checked_posts[username] = post_id

        return None

    # پست جدید پیدا شد
    if checked_posts[username] != post_id:

        checked_posts[username] = post_id

        return {
            "username": username,
            "text": latest.title,
            "link": latest.link
        }

    return None


def monitor_accounts(callback):

    print("👀 X Monitor Started")

    while True:

        try:
            accounts = get_accounts()

            print(
                f"🔎 Checking {len(accounts)} X account(s)..."
            )

            for account in accounts:

                result = check_account(account)

                if result:
                    print(
                        f"🚨 New post detected from @{account}"
                    )

                    callback(result)

        except Exception as e:

            print(
                f"❌ X Monitor error: {e}"
            )

        # بررسی هر 5 دقیقه
        time.sleep(300)
```

