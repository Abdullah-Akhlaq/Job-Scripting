# scrapers/linkedin.py
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
    "werkstudent data science Munich",
    "werkstudent machine learning Munich",
    "werkstudent python developer Munich",
    "werkstudent IT Munich",
]

def fetch():
    jobs = []
    for query in SEARCHES:
        url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={query.replace(' ', '%20')}"
            "&location=Munich%2C%20Bavaria%2C%20Germany"
            "&f_TPR=r86400"    # posted in last 24 hours
            "&f_JT=P"          # P = part-time (Werkstudent)
            "&start=0"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.find_all("div", class_="base-card")
            for card in cards:
                title_el   = card.find("h3", class_="base-search-card__title")
                company_el = card.find("h4", class_="base-search-card__subtitle")
                location_el= card.find("span", class_="job-search-card__location")
                date_el    = card.find("time")
                link_el    = card.find("a", class_="base-card__full-link")

                if title_el and link_el:
                    jobs.append({
                        "title":    title_el.get_text(strip=True),
                        "company":  company_el.get_text(strip=True) if company_el else "Unknown",
                        "location": location_el.get_text(strip=True) if location_el else "München",
                        "date":     date_el.get("datetime", "") if date_el else "",
                        "link":     link_el.get("href", "").split("?")[0],  # strip tracking params
                        "source":   "LinkedIn"
                    })
            print(f"[LinkedIn] '{query}': {len(cards)} cards found")
            time.sleep(2)   # be polite — 2 second delay between queries

        except Exception as e:
            print(f"[LinkedIn] ERROR for '{query}': {e}")
    return jobs