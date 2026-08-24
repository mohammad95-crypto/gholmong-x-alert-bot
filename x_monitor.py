import feedparser
import time


checked_posts = {}


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


def monitor_accounts(accounts, callback):

    while True:

        for account in accounts:

            result = check_account(account)

            if result:
                callback(result)

        time.sleep(300)
