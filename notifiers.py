import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"   # from @BotFather on Telegram
CHAT_ID = "YOUR_CHAT_ID"       # from @userinfobot

def send_telegram(jobs):
    if not jobs:
        return
    msg = f"🤖 *{len(jobs)} new Werkstudent jobs today!*\n\n"
    for j in jobs[:15]:  # max 15 per message
        msg += f"• [{j['title']}]({j['link']}) — {j['company']} _{j['source']}_\n"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )