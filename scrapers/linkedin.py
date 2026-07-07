import requests
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8",
}

SEARCHES = [
    "werkstudent software developer Munich",
    "Werkstudent Webentwickler",
    "Werkstudent Softwareentwicklung JavaScript",
    "werkstudent data science Munich",
    "working student frontend Munich",
    "werkstudent fullstack Munich",
    "werkstudent AI automation",
    "werkstudent IT Munich",
    "werkstudent machine learning Munich",
    "werkstudent python developer Munich",
    "internship software developer Munich",
    "internship data science Munich",
    "internship frontend Munich",
    "internship fullstack Munich",
]

def fetch():
    jobs = []
    seen_links = set()   # FIX 1: dedup within this run

    for query in SEARCHES:
        # FIX 2: removed &f_JT=P — that filter drops many valid Werkstudent
        # postings that LinkedIn tags as "Internship" or leaves untagged.
        # The keyword "werkstudent" in the query is enough to target them.
        url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={query.replace(' ', '%20')}"
            "&location=Munich%2C%20Bavaria%2C%20Germany"
            "&f_TPR=r86400"    # posted in last 24 hours only
            "&start=0"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.find_all("div", class_="base-card")
            new_this_query = 0

            for card in cards:
                title_el    = card.find("h3", class_="base-search-card__title")
                company_el  = card.find("h4", class_="base-search-card__subtitle")
                location_el = card.find("span", class_="job-search-card__location")
                date_el     = card.find("time")
                link_el     = card.find("a", class_="base-card__full-link")

                if not (title_el and link_el):
                    continue

                link = link_el.get("href", "").split("?")[0]

                # FIX 1: skip if already collected from a previous query
                if link in seen_links:
                    continue
                seen_links.add(link)

                jobs.append({
                    "title":    title_el.get_text(strip=True),
                    "company":  company_el.get_text(strip=True) if company_el else "Unknown",
                    "location": location_el.get_text(strip=True) if location_el else "München",
                    "date":     date_el.get("datetime", "") if date_el else "",
                    "link":     link,
                    "source":   "LinkedIn"
                })
                new_this_query += 1

            print(f"[LinkedIn] '{query}': {len(cards)} cards, {new_this_query} new unique")
            time.sleep(2)

        except Exception as e:
            print(f"[LinkedIn] ERROR for '{query}': {e}")

    print(f"[LinkedIn] Total unique: {len(jobs)}")
    return jobs