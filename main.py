from scrapers.arbeitsagentur import fetch as fetch_ba
from scrapers.rss_scraper     import fetch as fetch_rss       # StepStone + Indeed
from scrapers.linkedin        import fetch as fetch_linkedin
from scrapers.remotive        import fetch as fetch_remotive
from filter                   import filter_new_jobs
from notifiers                 import send

FETCHERS = [
    ("Arbeitsagentur", fetch_ba),
    ("StepStone + Indeed RSS", fetch_rss),
    ("LinkedIn", fetch_linkedin),
    ("Remotive", fetch_remotive),
]

def main():
    all_jobs = []
    for name, fn in FETCHERS:
        try:
            jobs = fn()
            print(f"[{name}] {len(jobs)} jobs fetched")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"[{name}] FAILED — {e}")

    new_jobs = filter_new_jobs(all_jobs)
    send(new_jobs, {"total_fetched": len(all_jobs), "sources": len(FETCHERS)})

if __name__ == "__main__":
    main()