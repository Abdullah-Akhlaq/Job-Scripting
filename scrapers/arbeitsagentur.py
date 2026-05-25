import requests

def fetch_arbeitsagentur_jobs():
    url = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
    params = {
        "was": "Werkstudent Software",
        "wo": "München",
        "angebotsart": 4,  # 4 = Werkstudent
        "size": 25
    }
    headers = {"X-API-Key": "jobboerse-jobsuche"}  # public key
    r = requests.get(url, params=params, headers=headers)
    jobs = []
    for job in r.json().get("stellenangebote", []):
        jobs.append({
            "title": job["titel"],
            "company": job["arbeitgeber"],
            "link": f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{job['hashId']}",
            "date": job["aktuelleVeroeffentlichungsdatum"],
            "source": "Arbeitsagentur"
        })
    return jobs