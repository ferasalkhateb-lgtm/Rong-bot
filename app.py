from flask import Flask, request, jsonify
import requests
import os
app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "rong123")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_ID = os.getenv("PHONE_ID", "")
MENU = """*منيو رونق الضيافة - المبرز* 🍽️
مندي لحم - 35 ريال
مندي دجاج - 25 ريال
مدفون لحم - 38 ريال
كبسة رونق - 28 ريال
للطلب اكتب: اطلب + اسم الطبق"""
def send_whatsapp(to, text):
    if not WHATSAPP_TOKEN or not PHONE_ID: return
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, headers=headers, json=data)
@app.route("/", methods=["GET"])
def home():
    return "Rong Bot Running"
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "fail", 403
    data = request.get_json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            frm = msg["from"]
            text = msg.get("text", {}).get("body", "").lower()
            if "منيو" in text or "menu" in text or "هلا" in text:
                send_whatsapp(frm, MENU)
            elif "اطلب" in text:
                send_whatsapp(frm, f"تم استلام: {text} - بنتواصل معك")
            else:
                send_whatsapp(frm, "اهلا في رونق 🌟 اكتب *منيو*")
    except: pass
    return jsonify({"status":"ok"}), 200
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
