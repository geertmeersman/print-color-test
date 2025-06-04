import os
import smtplib
import sys
import requests
from email.message import EmailMessage

status = sys.argv[1]  # "SUCCESS" or "FAILURE"
message_text = sys.argv[2]

# ---- Icons ----
icons = {
    "SUCCESS": "✅",
    "FAILURE": "❌"
}
icon = icons.get(status.upper(), "ℹ️")

# ---- Printer info ----
PRINTER_NAME = os.getenv("PRINTER_NAME")

# ---- Email Setup ----
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PWD = os.getenv("SMTP_PWD")


# ---- Telegram Setup ----
TELEGRAM_BOT_ID = os.getenv("TELEGRAM_BOT_ID")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_WEBHOOK = f"https://api.telegram.org/bot{TELEGRAM_BOT_ID}/sendMessage"

# ---- Email Notification ----
if SMTP_SERVER:
    try:
        msg = EmailMessage()
        msg["Subject"] = f"[{PRINTER_NAME}] Print color page {status}"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        msg.set_content(f"{icon} {message_text}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PWD)
            server.send_message(msg)
        print("[INFO] Email sent.")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")

# ---- Telegram Notification ----
if TELEGRAM_BOT_ID:
    try:
        payload = {
            "text": f"{icon} *[{PRINTER_NAME}] {status}*\n{message_text}",
            "chat_id": TELEGRAM_CHAT_ID,
            "parse_mode": "Markdown"
        }
        response = requests.post(TELEGRAM_WEBHOOK, json=payload)
        if response.status_code != 200:
            raise Exception(response.text)
        print("[INFO] Telegram message sent.")
    except Exception as e:
        print(f"[ERROR] Telegram notification failed: {e}")
