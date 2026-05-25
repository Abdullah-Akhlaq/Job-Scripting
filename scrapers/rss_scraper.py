# scrapers/rss_scraper.py
import feedparser

FEEDS = {
    "StepStone": [
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+Software&location=M%C3%BCnchen",
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+Data+Science&location=M%C3%BCnchen",
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+Python&location=M%C3%BCnchen",
        "https://www.stepstone.de/rss/jobsearch.html?keywords=Werkstudent+IT&location=M%C3%BCnchen",
    ],
    "Indeed": [
        "https://de.indeed.com/rss?q=werkstudent+software+developer&l=M%C3%BCnchen",
        "https://de.indeed.com/rss?q=werkstudent+data+science&l=M%C3%BCnchen",
        "https://de.indeed.com/rss?q=werkstudent+machine+learning&l=M%C3%BCnchen",
        "https://de.indeed.com/rss?q=werkstudent+python&l=M%C3%BCnchen",
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
                        "title":    entry.get("title", "N/A"),
                        "company":  entry.get("author", "Unknown"),
                        "location": "München",
                        "date":     entry.get("published", ""),
                        "link":     entry.get("link", ""),
                        "source":   source
                    })
                print(f"[{source}] {url[-40:]}: {len(feed.entries)} jobs")
            except Exception as e:
                print(f"[{source}] ERROR: {e}")
    return jobs