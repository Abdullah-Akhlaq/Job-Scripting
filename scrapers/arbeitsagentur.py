
import requests

def fetch(location="München"):
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    headers = {"X-API-Key": "jobboerse-jobsuche"}

    terms = ["Werkstudent Software", "Werkstudent IT",
             "Werkstudent Data Science", "Werkstudent Python",
             "Werkstudent Machine Learning", "Werkstudent AI"]
    jobs, seen = [], set()
    for term in terms:
        try:
            r = requests.get(url, headers=headers, timeout=10, params={
                "was": term, "wo": location, "angebotsart": 4, "size": 15
            })
            for job in r.json().get("stellenangebote", []):
                hid = job.get("hashId")
                if hid and hid not in seen:
                    seen.add(hid)
                    jobs.append({
                        "title":   job.get("titel", "N/A"),
                        "company": job.get("arbeitgeber", "Unknown"),
                        "location":job.get("arbeitsort", {}).get("ort", location),
                        "date":    job.get("aktuelleVeroeffentlichungsdatum", ""),
                        "link":    f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{hid}",
                        "source":  "Arbeitsagentur"
                    })
        except Exception as e:
            print(f"[arbeitsagentur] {term}: {e}")
    return jobs
