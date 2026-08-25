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
        "SELECT username FROM accounts"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [x[0] for x in rows]



def check_account(username):

    url = f"https://nitter.net/{username}/rss"

    feed = feedparser.parse(url)


    if not feed.entries:
        return None


    latest = feed.entries[0]

    post_id = latest.get("id")


    if username not in checked_posts:

        checked_posts[username] = post_id

        return None


    if checked_posts[username] != post_id:

        checked_posts[username] = post_id

        return {
            "username": username,
            "text": latest.title,
            "link": latest.link
        }


    return None



def monitor_accounts(callback):

    while True:

        accounts = get_accounts()


        for account in accounts:

            result = check_account(account)

            if result:
                callback(result)


        time.sleep(300)
