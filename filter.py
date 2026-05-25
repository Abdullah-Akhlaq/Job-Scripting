import sqlite3

KEYWORDS = ["software", "developer", "python", "data", "ai", "machine learning",
            "backend", "frontend", "it", "werkstudent", "cloud", "devops"]

def is_relevant(title):
    return any(kw in title.lower() for kw in KEYWORDS)

def is_new(job, db_path="jobs.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS seen (link TEXT PRIMARY KEY)")
    cur.execute("SELECT 1 FROM seen WHERE link=?", (job["link"],))
    exists = cur.fetchone()
    if not exists:
        cur.execute("INSERT INTO seen VALUES (?)", (job["link"],))
        conn.commit()
    conn.close()
    return not exists