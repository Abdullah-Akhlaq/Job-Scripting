import requests

def fetch():
    """Remotive — free remote jobs API, good for AI/ML/Data roles."""
    categories = ["software-dev", "data", "devops-sysadmin"]
    jobs = []
    for cat in categories:
        try:
            r = requests.get(
                "https://remotive.com/api/remote-jobs",
                params={"category": cat, "limit": 20},
                timeout=10
            )
            for job in r.json().get("jobs", []):
                jobs.append({
                    "title":    job.get("title", "N/A"),
                    "company":  job.get("company_name", "Unknown"),
                    "location": job.get("candidate_required_location", "Remote"),
                    "date":     job.get("publication_date", ""),
                    "link":     job.get("url", ""),
                    "source":   "Remotive"
                })
        except Exception as e:
            print(f"[remotive] {cat}: {e}")
    return jobs