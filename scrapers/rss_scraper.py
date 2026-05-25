import feedparser

FEEDS = {
    "Indeed": [
        "https://de.indeed.com/rss?q=werkstudent+software&l",
        "https://de.indeed.com/rss?q=werkstudent+data+science&l",
        "https://de.indeed.com/rss?q=werkstudent+IT&l",
        "https://de.indeed.com/rss?q=werkstudent+python&l",
    ],
    "StepStone": [
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+Software",
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+Data+Science",
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+IT",
    ],
    "LinkedIn": [
        "https://www.linkedin.com/jobs/search/?keywords=werkstudent+software+developer",
    ],
    "Glassdoor": [
        "https://www.glassdoor.de/Job/münchen-werkstudent-software-jobs-SRCH_IL.0,7_IC2659660_KO8,28.htm",
    ],
}

def fetch():
    jobs = []
    for source, urls in FEEDS.items():
        for url in urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    jobs.append({
                        "title":   entry.get("title", "N/A"),
                        "company": entry.get("author", entry.get("company", "Unknown")),
                        "location": "München",
                        "date":    entry.get("published", ""),
                        "link":    entry.get("link", ""),
                        "source":  source
                    })
            except Exception as e:
                print(f"[rss:{source}] {url[:50]}: {e}")
    return jobs