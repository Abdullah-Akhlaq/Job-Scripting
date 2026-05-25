import os
import requests

def send_telegram(jobs):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not bot_token or not chat_id:
        print("[ERROR] Missing Telegram BOT_TOKEN or CHAT_ID environment variables.")
        return

    # Case: No jobs found, but send status ping anyway
    if not jobs:
        print("[INFO] No new jobs found. Sending ping confirmation to Telegram...")
        message = "✅ **Job Hunt Status:** Automation executed successfully! No brand-new positions matched your criteria today."
        _dispatch_message(bot_token, chat_id, message)
        return

    # Case: New jobs found
    print(f"[INFO] Sending {len(jobs)} jobs to Telegram...")
    for job in jobs:
        message = (
            f"🔍 **New Job Found!**\n\n"
            f"💼 **Title:** {job['title']}\n"
            f"🏢 **Company:** {job['company']}\n"
            f"📍 **Location:** {job['location']}\n"
            f"📅 **Date:** {job['date']}\n"
            f"🔗 [View Job Posting]({job['link']})"
        )
        _dispatch_message(bot_token, chat_id, message)

def _dispatch_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")