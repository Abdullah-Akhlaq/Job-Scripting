import os 
from scrapers.arbeitsagentur import fetch as fetch_arbeitsagentur
from scrapers.rss_scraper     import fetch as fetch_rss
from scrapers.remotive        import fetch as fetch_remotive
from filter import filter_new_jobs
from notifiers import send_telegram

def main():
    print("=" * 40)
    print("JOB HUNTER STARTED")
    print("=" * 40)

    # ── 1. Fetch from all sources ──────────────
    all_jobs = []
    fetchers = [
        ("Arbeitsagentur", fetch_arbeitsagentur),
        ("RSS (Indeed/StepStone/LinkedIn)", fetch_rss),
        ("Remotive", fetch_remotive),
    ]
    for name, fn in fetchers:
        try:
            jobs = fn()
            print(f"[{name}] fetched {len(jobs)} jobs")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"[{name}] FAILED: {e}")

    print(f"\nTotal fetched (before filter): {len(all_jobs)}")

    # ── 2. Filter, deduplicate, score ──────────
    new_jobs = filter_new_jobs(all_jobs)
    print(f"New relevant jobs (after filter): {len(new_jobs)}")

    # ── 3. Send to Telegram ────────────────────
    stats = {
        "total_fetched": len(all_jobs),
        "sources": len(set(j["source"] for j in all_jobs))
    }
    send(new_jobs, stats)
    print("\nTelegram notification sent ✅")
    print("=" * 40)

if __name__ == "__main__":
    main()