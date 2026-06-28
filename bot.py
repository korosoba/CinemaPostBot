"""
Telegram bot: receives a URL, returns a ready-to-publish post with image.
Deployed on Render as a Web Service (webhook mode).
Only responds to ALLOWED_USER_ID for security.
"""

import os
import logging
import urllib.request
import urllib.parse
import json

from flask import Flask, request, Response

from article_parser import parse_article
from post_generator import generate_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USER_ID = int(os.environ["ALLOWED_USER_ID"])  # your Telegram user ID
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ── Telegram API helpers ──────────────────────────────────────────────────────

def tg_send(method: str, payload: dict):
    url = f"{API_BASE}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def send_message(chat_id: int, text: str):
    tg_send("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    })


def send_photo_with_caption(chat_id: int, image_url: str, caption: str):
    """Send photo with post text as caption (max 1024 chars)."""
    tg_send("sendPhoto", {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "HTML",
    })


def send_post(chat_id: int, post_text: str, image_url: str | None, source_url: str):
    """Send the generated post, with image if available."""
    # Append source link at the end
    full_text = f"{post_text}\n\n🔗 <a href=\"{source_url}\">Источник</a>"

    if image_url:
        try:
            # Caption limit in Telegram is 1024 chars
            caption = full_text[:1024]
            send_photo_with_caption(chat_id, image_url, caption)
            # If post text is longer than caption limit, send remainder as text
            if len(full_text) > 1024:
                send_message(chat_id, full_text[1024:])
            return
        except Exception as e:
            logger.warning(f"Failed to send photo ({e}), falling back to text only")

    # No image or photo send failed — send as plain text
    send_message(chat_id, full_text[:4096])


# ── URL detection ─────────────────────────────────────────────────────────────

def extract_url(text: str) -> str | None:
    """Find a URL in the message text."""
    for word in text.split():
        if word.startswith("http://") or word.startswith("https://"):
            return word
    return None


# ── Webhook handler ───────────────────────────────────────────────────────────

@app.route(f"/webhook", methods=["POST"])
def webhook():
    # Optional secret header check
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if token != WEBHOOK_SECRET:
            return Response("Forbidden", status=403)

    update = request.get_json(silent=True)
    if not update:
        return Response("OK", status=200)

    message = update.get("message") or update.get("edited_message")
    if not message:
        return Response("OK", status=200)

    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "").strip()

    # Security: ignore everyone except you
    if user_id != ALLOWED_USER_ID:
        logger.warning(f"Ignored message from user_id={user_id}")
        return Response("OK", status=200)

    if not text:
        return Response("OK", status=200)

    url = extract_url(text)
    if not url:
        send_message(chat_id, "👋 Пришли мне ссылку на статью — сделаю пост для канала.")
        return Response("OK", status=200)

    # Processing pipeline
    send_message(chat_id, "⏳ Читаю статью...")

    try:
        article = parse_article(url)
        if not article:
            send_message(chat_id, "❌ Не удалось прочитать статью. Попробуй другую ссылку.")
            return Response("OK", status=200)

        send_message(chat_id, "✍️ Пишу пост...")
        post_text = generate_post(article)
        send_post(chat_id, post_text, article.image_url, url)

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        send_message(chat_id, f"❌ Ошибка: {e}")

    return Response("OK", status=200)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/")
def index():
    return {"bot": "Cinema Post Bot", "status": "running"}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
