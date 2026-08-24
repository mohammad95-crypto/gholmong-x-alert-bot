from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "GHOLMONG X Alert Bot is running!"

def keep_alive():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=keep_alive).start()

    while True:
        print("GHOLMONG Alert Bot Running...")
        time.sleep(60)
