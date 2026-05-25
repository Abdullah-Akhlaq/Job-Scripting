import feedparser

def fetch_indeed_jobs(query="werkstudent software", location="Munich"):
    url = f"https://de.indeed.com/rss?q={query.replace(' ', '+')}&l={location}"
    feed = feedparser.parse(url)
    jobs = []
    for entry in feed.entries:
        jobs.append({
            "title": entry.title,
            "company": entry.get("author", "Unknown"),
            "link": entry.link,
            "date": entry.get("published", ""),
            "source": "Indeed"
        })
    return jobs