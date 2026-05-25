import os
import requests

def send_telegram(jobs):
    bot_token = "8923705038:AAFHDQIFco37Kd7uanjcAOTGEpegvt6Y_jM"
    chat_id = "8923705038"


    if not bot_token or not chat_id:
        print("[ERROR] Missing Telegram BOT_TOKEN or CHAT_ID environment variables.")
        return

    # Case: No jobs found, but send status ping anyway
    if not jobs:
        print("[INFO] No new jobs found. Sending HTML status ping to Telegram...")
        message = "✅ <b>Job Hunt Status:</b> Automation executed successfully! No brand-new positions matched your criteria today."
        _dispatch_message(bot_token, chat_id, message)
        return

    # Case: New jobs found
    print(f"[INFO] Sending {len(jobs)} jobs to Telegram...")
    for job in jobs:
        # Using bulletproof HTML strings instead of unstable Markdown
        message = (
            f"🔍 <b>New Job Found!</b>\n\n"
            f"💼 <b>Title:</b> {job['title']}\n"
            f"🏢 <b>Company:</b> {job['company']}\n"
            f"📍 <b>Location:</b> {job['location']}\n"
            f"📅 <b>Date:</b> {job['date']}\n"
            f"🔗 <a href='{job['link']}'>View Job Posting</a>"
        )
        _dispatch_message(bot_token, chat_id, message)

def _dispatch_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"  # <-- Switched to HTML parsing
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        
        # Explicit print statement to see the exact Telegram API feedback in GitHub logs
        print(f"[TELEGRAM API RESPONSE] Status: {r.status_code} | Response: {r.text}")
        
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")