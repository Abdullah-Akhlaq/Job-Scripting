import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram(jobs: list):
    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    today = datetime.now().strftime("%d.%m.%Y")

    if not jobs:
        msg = (
            f"🔍 *Job Hunt Report — {today}*\n\n"
            f"No new Werkstudent jobs found today.\n"
            f"Will check again tomorrow at 8:00 AM ✅"
        )
        requests.post(base_url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        })
        return

    # Send header message first
    header = (
        f"🚀 *Job Hunt Report — {today}*\n"
        f"Found *{len(jobs)} new jobs* on Arbeitsagentur!\n"
        f"{'─' * 28}"
    )
    requests.post(base_url, json={
        "chat_id": CHAT_ID,
        "text": header,
        "parse_mode": "Markdown"
    })

    # Send jobs in batches of 5 to avoid message size limits
    for i in range(0, len(jobs), 5):
        batch = jobs[i:i+5]
        msg = ""
        for j in batch:
            msg += (
                f"\n💼 *{j['title']}*\n"
                f"🏢 {j['company']}\n"
                f"📍 {j['location']}\n"
                f"📅 {j['date']}\n"
                f"🔗 [View Job]({j['link']})\n"
                f"{'─' * 28}\n"
            )
        requests.post(base_url, json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        })

    # Send footer
    footer = "✅ *That's all for today! Good luck! 🍀*"
    requests.post(base_url, json={
        "chat_id": CHAT_ID,
        "text": footer,
        "parse_mode": "Markdown"
    })