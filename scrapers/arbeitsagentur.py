import requests

def fetch_jobs():
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    
    search_terms = [
        "Werkstudent Software",
        "Werkstudent IT",
        "Werkstudent Data Science",
        "Werkstudent AI",
        "Werkstudent Python",
        "Werkstudent Machine Learning",
        "Werkstudent Backend",
        "Werkstudent Frontend",
        "Werkstudent Cloud",
        "Werkstudent DevOps"
        
    ]
    
    headers = {"X-API-Key": "jobboerse-jobsuche"}
    all_jobs = []
    seen_ids = set()

    for term in search_terms:
        params = {
            "was": term,
            "angebotsart": 4,      # 4 = Werkstudent
            "size": 20,            # Increased to grab more fresh entries nationwide
        }
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            for job in data.get("stellenangebote", []):
                job_id = job.get("hashId")
                if job_id and job_id not in seen_ids:
                    seen_ids.add(job_id)
                    all_jobs.append({
                        "title": job.get("titel", "N/A"),
                        "company": job.get("arbeitgeber", "Unknown"),
                        "location": job.get("arbeitsort", {}).get("ort", "N/A"),
                        "date": job.get("aktuelleVeroeffentlichungsdatum", "N/A"),
                        "link": f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{job_id}",
                        "source": "Arbeitsagentur"
                    })
        except Exception as e:
            print(f"[ERROR] Failed to fetch '{term}': {e}")

    print(f"[INFO] Total jobs fetched: {len(all_jobs)}")
    return all_jobs