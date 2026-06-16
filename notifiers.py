
# notifiers.py
import os
import json
import requests
from datetime import datetime

def send(jobs, stats):
    """
    Send filtered jobs to Telegram with nice formatting.
    
    Args:
        jobs: List of job dictionaries with title, company, link, description, priority, etc.
        stats: Dictionary with metadata (total_fetched, sources)
    """
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    
    if not bot_token or not chat_id:
        print("[ERROR] BOT_TOKEN or CHAT_ID not set in environment")
        return

    if not jobs:
        message = (
            "🔍 *Daily Job Hunt* (8 AM)\n\n"
            "❌ No matching jobs found today.\n\n"
            f"📊 Stats:\n"
            f"• Total scanned: {stats.get('total_fetched', 0)}\n"
            f"• Sources: {stats.get('sources', 0)}\n"
            f"• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        send_telegram_message(bot_token, chat_id, message)
        return

    # Group jobs by priority
    priority_groups = {}
    for job in jobs:
        priority = job.get("priority", 5)
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(job)

    # Priority labels
    priority_labels = {
        1: "🔥 TOP PRIORITY - Werkstudent/Internship (Perfect Match)",
        2: "⭐ HIGH PRIORITY - IT/Admin Student Roles",
        3: "👍 GOOD - General Student Developer Roles",
        4: "📌 MEDIUM - Standard IT/Software Roles",
        5: "📍 LOW - Other Roles"
    }

    # Send header
    header = (
        f"🔍 *Daily Job Hunt* - {datetime.now().strftime('%Y-%m-%d')}\n"
        f"✅ Found *{len(jobs)}* matching jobs!\n\n"
        f"📊 Stats:\n"
        f"• Total scanned: {stats.get('total_fetched', 0)}\n"
        f"• Sources: {stats.get('sources', 0)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    send_telegram_message(bot_token, chat_id, header)

    # Send jobs grouped by priority
    job_count = 1
    for priority in sorted(priority_groups.keys()):
        jobs_in_priority = priority_groups[priority]
        
        priority_header = f"\n{priority_labels.get(priority, 'Other Jobs')}\n"
        priority_header += "━" * 40 + "\n"
        send_telegram_message(bot_token, chat_id, priority_header)

        for job in jobs_in_priority:
            message = format_job_message(job, job_count)
            send_telegram_message(bot_token, chat_id, message)
            job_count += 1

    # Send footer with application tips
    footer = (
        "\n" + "━" * 40 + "\n"
        "💡 *Tips for applying:*\n"
        "• Customize your cover letter for each job\n"
        "• Highlight relevant projects & skills\n"
        "• Follow up after 1 week if no response\n"
        "• Keep a spreadsheet of applications\n\n"
        "🎯 *Good luck with your applications!* 💪\n"
        f"Next hunt: Tomorrow at 8 AM (German time)"
    )
    send_telegram_message(bot_token, chat_id, footer)

def format_job_message(job, number):
    """
    Format a single job for Telegram message.
    """
    title = job.get("title", "Unknown")
    company = job.get("company", "Unknown")
    location = job.get("location", "Unknown")
    link = job.get("link", "")
    date_posted = job.get("date", "")
    description = job.get("description", "")
    source = job.get("source", "Unknown")

    # Clean up date if it exists
    if date_posted:
        try:
            date_obj = datetime.fromisoformat(date_posted)
            date_posted = date_obj.strftime("%d.%m.%Y")
        except:
            pass

    # Truncate description if too long
    if description:
        # Get first 300 characters or first 2 sentences
        sentences = description.split(". ")
        if len(sentences) > 1:
            description = ". ".join(sentences[:2]) + "."
        else:
            description = description[:300] + "..." if len(description) > 300 else description
    else:
        description = "_No description available_"

    message = (
        f"*{number}. {title}*\n"
        f"🏢 {company}\n"
        f"📍 {location}\n"
        f"📅 {date_posted}\n"
        f"🔗 Source: {source}\n\n"
        f"📝 *Overview:*\n"
        f"_{description}_\n\n"
        f"🔗 [Apply on {source}]({link})\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    return message

def send_telegram_message(bot_token, chat_id, message):
    """
    Send a message to Telegram using the Bot API.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[Telegram] ✓ Message sent")
        else:
            print(f"[Telegram] ✗ Failed to send message: {response.status_code}")
            print(f"[Telegram] Response: {response.text}")
    except Exception as e:
        print(f"[Telegram] ✗ Error sending message: {e}")
