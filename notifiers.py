import requests, os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ["CHAT_ID"]
API       = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

SOURCE_ICONS = {
    "Arbeitsagentur": "🏛",
    "Indeed":         "🔵",
    "StepStone":      "🟠",
    "LinkedIn":       "💼",
    "Glassdoor":      "🟢",
    "Remotive":       "🌐",
}

def _send(text: str):
    requests.post(API, json={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    })

def send(jobs: list, stats: dict):
    today = datetime.now().strftime("%d.%m.%Y")

    # ── Header ──────────────────────────────────────────────
    _send(
        f"🤖 *Job Hunt — {today}*\n"
        f"Scanned *{stats['total_fetched']}* listings across *{stats['sources']}* platforms\n"
        f"✅ *{len(jobs)} new relevant jobs* after filtering\n"
        f"{'─' * 30}"
    )

    if not jobs:
        _send("No new jobs today. Will check again tomorrow at 8 AM ✅")
        return

    # ── Source breakdown ────────────────────────────────────
    breakdown = {}
    for j in jobs:
        breakdown[j["source"]] = breakdown.get(j["source"], 0) + 1
    lines = [f"{SOURCE_ICONS.get(s,'•')} {s}: *{n}*" for s, n in breakdown.items()]
    _send("📊 *Sources breakdown*\n" + "\n".join(lines))

    # ── Jobs in batches of 5 ────────────────────────────────
    for i in range(0, min(len(jobs), 30), 5):   # cap at 30 jobs max
        batch = jobs[i:i+5]
        msg = ""
        for j in batch:
            stars = "⭐" * min(j.get("score", 1), 3)
            icon  = SOURCE_ICONS.get(j["source"], "•")
            msg += (
                f"\n{stars} *{j['title']}*\n"
                f"{icon} {j['source']}  🏢 {j['company']}\n"
                f"📍 {j['location']}\n"
                f"🔗 [View Job]({j['link']})\n"
                f"{'─' * 30}\n"
            )
        _send(msg)

    # ── Footer ──────────────────────────────────────────────
    _send(
        f"✅ *Done for today! Good luck! 🍀*\n"
        f"_{len(jobs)} jobs shown · sorted by relevance · duplicates removed_"
    )