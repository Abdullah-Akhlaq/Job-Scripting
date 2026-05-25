import os
import json

DB_FILE = "seen_jobs.json"

def filter_new_jobs(jobs):
    seen_links = set()
    
    # Load already seen job links if the file exists
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                seen_links = set(json.load(f))
        except Exception as e:
            print(f"[WARNING] Could not read cache file: {e}")

    # Filter out jobs we've already seen
    new_jobs = [job for job in jobs if job["link"] not in seen_links]

    # Update our tracker with the new jobs
    for job in new_jobs:
        seen_links.add(job["link"])

    try:
        with open(DB_FILE, "w") as f:
            json.dump(list(seen_links), f)
    except Exception as e:
        print(f"[ERROR] Could not save cache file: {e}")

    print(f"[INFO] Filtered down to {len(new_jobs)} new jobs.")
    return new_jobs