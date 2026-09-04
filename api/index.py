import os
import json
import requests
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_KEY = os.environ.get("LLM_API_KEY")
API_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
MODEL_NAME = os.environ.get("LLM_MODEL", "google/gemini-2.0-flash-001")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Bot is running 24/7 on Vercel!".encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = None

        if not data or "message" not in data:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ignored"}).encode('utf-8'))
            return

        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        if user_text.startswith("/start"):
            reply = "Halo bro! Bot AI kamu aktif 24/7 di Vercel."
        elif user_text:
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
                r = requests.post(API_URL, headers=headers, json=payload, timeout=40)
                res = r.json()
                reply = res["choices"][0]["message"]["content"]
            except Exception as e:
                reply = f"Error: {str(e)}"
        else:
            reply = "Pesan kosong."

        tg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(tg_url, json={"chat_id": chat_id, "text": reply})

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
