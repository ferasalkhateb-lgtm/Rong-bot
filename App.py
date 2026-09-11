from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "ronq123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("PHONE_ID", "")

MENU = """🍽️ *منيو رونق الضيافة - المبرز*
🥩 مندي لحم - 35 ريال
🍗 مندي دجاج - 25 ريال
🔥 مدفون لحم - 38 ريال
🍛 كبسة رونق الخاصة - 28 ريال
🥗 سلطات - 8 ريال

للطلب اكتب: اطلب + اسم الطبق
مثال: اطلب مندي لحم"""

def send_whatsapp(to, text):
    if not WHATSAPP_TOKEN or not PHONE_ID:
        print(f"الى {to}: {text}")
        return True
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    r = requests.post(url, headers=headers, json=data)
    return r.ok

@app.route("/")
def home():
    return "رونق الضيافة شغال ✅"

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "خطأ", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            from_number = msg["from"]
            text = msg.get("text", {}).get("body", "").lower()
            if "هلا" in text or "سلام" in text or "مرحبا" in text or "hi" in text:
                reply = "هلا والله حياك الله في رونق الضيافة ✨\nاكتب *منيو* عشان تشوف قائمتنا"
            elif "منيو" in text or "قائمة" in text:
                reply = MENU
            elif "اطلب" in text:
                reply = "تم ✅ ارسل موقعك ورقمك والكابتن جايك خلال 30 دقيقة 🚚\nللتواصل: 0509082647"
            elif "موقع" in text or "وين" in text:
                reply = "📍 المبرز - الأحساء\n⏰ 11ص الى 12 ليلاً\n🚚 توصيل سريع"
            else:
                reply = "حياك في رونق الضيافة 🌹\nاكتب *منيو* او *اطلب*"
            send_whatsapp(from_number, reply)
    except Exception as e:
        print(e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
