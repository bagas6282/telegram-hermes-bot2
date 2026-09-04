import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_KEY = os.environ.get("LLM_API_KEY")
API_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL_NAME = os.environ.get("LLM_MODEL", "google/gemini-2.0-flash-001")

@app.route("/", methods=["GET"])
def index():
    return "Bot is running 24/7!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True, silent=True)
    if not data or "message" not in data:
        return jsonify({"status": "ignored"}), 200

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    if not user_text:
        return jsonify({"status": "no text"}), 200

    if user_text.startswith("/start"):
        reply = "Halo bro! Bot AI kamu aktif 24/7."
    else:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a helpful and direct AI assistant."},
                {"role": "user", "content": user_text}
            ]
        }
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=45)
            res = r.json()
            reply = res["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"Error: {str(e)}"

    tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(tg_url, json={"chat_id": chat_id, "text": reply})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
