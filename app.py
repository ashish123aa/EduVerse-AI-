import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024  # allow photo uploads

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
IMG_TYPES = ("image/jpeg", "image/png", "image/webp", "image/gif")


def convert(m):
    """Turn the app's messages into Groq (OpenAI-style) messages. Returns (message, has_image)."""
    if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
        return None, False
    c = m.get("content")
    if isinstance(c, str):
        return ({"role": m["role"], "content": c[:20000]}, False) if c.strip() else (None, False)
    if isinstance(c, list) and m["role"] == "user":
        parts, has_img = [], False
        for b in c:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                parts.append({"type": "text", "text": str(b.get("text", ""))[:20000]})
            elif b.get("type") == "image":
                src = b.get("source") or {}
                if (src.get("type") == "base64" and src.get("media_type") in IMG_TYPES
                        and len(src.get("data", "")) < 5_000_000):
                    url = f"data:{src['media_type']};base64,{src['data']}"
                    parts.append({"type": "image_url", "image_url": {"url": url}})
                    has_img = True
        return ({"role": "user", "content": parts}, has_img) if parts else (None, False)
    return None, False


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/api/ai", methods=["POST"])
def ai():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return jsonify(text="AI key is not set. Add GROQ_API_KEY to the .env file and restart the app.")
    raw = (request.get_json(silent=True) or {}).get("messages", [])
    msgs, any_img = [], False
    for m in raw[-30:]:
        cm, img = convert(m)
        if cm:
            msgs.append(cm)
            any_img = any_img or img
    if not msgs:
        return jsonify(error="No messages received."), 400
    model = (os.getenv("GROQ_VISION_MODEL", "qwen/qwen3.8-27b") if any_img
             else os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"))
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "messages": msgs, "max_tokens": 4000, "temperature": 0.5},
            timeout=90,
        )
        data = r.json()
        if r.status_code == 429:
            return jsonify(text="AI rate limit reached. Please wait a minute and try again.")
        if r.status_code != 200:
            msg = (data.get("error") or {}).get("message", r.text[:200]) if isinstance(data, dict) else r.text[:200]
            return jsonify(text=f"AI error: {msg}")
        return jsonify(text=data["choices"][0]["message"]["content"])
    except Exception as e:
        return jsonify(text=f"AI error: {e}")


if __name__ == "__main__":
    print("EduVerse AI running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
