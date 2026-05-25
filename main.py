import os 
from scrapers.arbeitsagentur import fetch_jobs
from filter import filter_new_jobs
from notifiers import send_telegram

def main():
    print("=== Job Hunter Started ===")
    
    # Step 1: Fetch
    jobs = fetch_jobs()
    
    # Step 2: Filter (relevant + not seen before)
    new_jobs = filter_new_jobs(jobs)
    
    # Step 3: Notify
    send_telegram(new_jobs)
    
    print("=== Job Hunter Finished ===")

if __name__ == "__main__":
    main()