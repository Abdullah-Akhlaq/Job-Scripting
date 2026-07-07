# filter.py
# ─────────────────────────────────────────────────────────────────────────────
# Smart two-pass filter:
#
#   Pass 1 — HARD BLOCK (always drop regardless of anything else)
#             Only blocks jobs that are clearly senior/management
#
#   Pass 2 — RELEVANCE CHECK (keep if EITHER condition is met)
#     (a) Title contains a tech keyword (python, react, data science, …)
#     (b) Title contains a role-type keyword (developer, engineer, analyst, …)
#
#   This means a job titled "Werkstudent Softwareentwicklung" passes even
#   though "software" is not in the title — because "entwicklung" maps to dev.
#   A job titled "Werkstudent Data" also passes — broad but valid.
#   A job titled "Werkstudent Marketing" is dropped — no tech/role match.
#
#   MIN_SCORE is removed. Relevance is binary (pass/fail), then jobs are
#   sorted by a BONUS score that rewards more specific skill matches.
# ─────────────────────────────────────────────────────────────────────────────

import sqlite3

DB = "jobs.db"

# ── Hard blocklist — ONLY true senior/management titles ───────────────────────
# Keep this SHORT and SPECIFIC. Don't add broad words like "lead" or "head"
# because "lead developer" and "team lead" are different things.
HARD_BLOCK = [
    "head of",
    "vice president",
    "vp ",
    "chief ",
    "direktor",
    "bereichsleiter",
    "abteilungsleiter",
]

# ── Tech keywords — specific technologies you work with ──────────────────────
# If ANY of these appear in the title → job is relevant
TECH_KEYWORDS = [
    # Languages
    "python", "java", "javascript", "typescript", "js", "kotlin", "c++", "golang", "rust", "scala",
    # Frontend
    "react", "vue", "angular", "next.js", "nextjs", "html", "css", "frontend", "front-end",
    # Backend & infra
    "backend", "back-end", "node", "django", "flask", "spring", "fastapi", "rest", "api",
    "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "cloud", "devops", "ci/cd",
    "linux", "terraform", "ansible", "microservice",
    # Data & AI
    "python", "data science", "datascience", "machine learning", "machinelearning",
    "deep learning", "deeplearning", "neural", "nlp", "llm", "ai ", "künstliche intelligenz",
    "data engineer", "data analyst", "dataengineer", "analytics", "tableau", "powerbi",
    "sql", "postgresql", "mysql", "mongodb", "spark", "hadoop", "etl",
    # General software
    "software", "fullstack", "full stack", "full-stack",
    "mobile", "android", "ios", "flutter", "swift",
    "web development", "webentwicklung",
]

# ── Role-type keywords — German + English job role words ─────────────────────
# If ANY of these appear → job is a tech role even without specific tech name
ROLE_KEYWORDS = [
    # German role words (very common in German job titles)
    "softwareentwicklung", "softwareentwickler", "entwickler", "entwicklung",
    "informatik", "informatiker", "systemadministrator", "systemadmin",
    "netzwerk", "datenbank", "datenbankentwickler",
    "anwendungsentwickler", "anwendungsentwicklung",
    "webentwickler", "appentwickler", "it-administrator",
    "datenwissenschaft", "maschinelles lernen",
    # English role words
    "developer", "engineer", "programmer", "architect", "analyst",
    "data scientist", "ml engineer", "ai engineer", "devops engineer",
    "sysadmin", "sys admin", "site reliability", "sre",
    # General
    " it ", " it\n", "(it)", "it-", "-it ", "i.t.", " tech", "technologie", "technology",
    "coding", "coder", "programming",
]


def _is_it_only(title: str) -> bool:
    """Special case: title ends with 'IT' or 'IT ' — e.g. 'Werkstudent IT'."""
    import re
    return bool(re.search(r'\bit\b', title.lower()))

# ── Bonus scoring — rewards more specific / senior-student roles ──────────────
# These don't gate anything, just sort results better
BONUS_SCORE = {
    "machine learning": 5, "deep learning": 5, "data science": 5,
    "llm": 5, "nlp": 5, "ai ": 4, "neural": 4,
    "python": 4, "react": 4, "typescript": 4, "javascript": 4,
    "aws": 3, "kubernetes": 3, "docker": 3, "cloud": 3, "devops": 3,
    "java": 3, "backend": 3, "frontend": 3, "fullstack": 3,
    "sql": 2, "developer": 2, "engineer": 2, "software": 2,
    "it ": 1, "analyst": 1,
}


def _is_blocked(title: str) -> bool:
    t = title.lower()
    return any(b in t for b in HARD_BLOCK)


def _is_relevant(title: str) -> bool:
    t = title.lower()
    return (
        any(k in t for k in TECH_KEYWORDS) or
        any(k in t for k in ROLE_KEYWORDS) or
        _is_it_only(title)   # catches "Werkstudent IT", "Werkstudent IT-Support" etc.
    )


def _bonus(title: str) -> int:
    t = title.lower()
    return sum(v for k, v in BONUS_SCORE.items() if k in t)


def _init_db(con):
    con.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            link      TEXT PRIMARY KEY,
            title     TEXT,
            source    TEXT,
            seen_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()


def filter_new_jobs(jobs: list) -> list:
    """
    Returns new, relevant, unseen jobs sorted by bonus score (best first).
    Never misses a real job due to overly strict keyword matching.
    """
    con = sqlite3.connect(DB)
    _init_db(con)
    cur = con.cursor()

    passed, blocked, irrelevant, duplicate = [], 0, 0, 0

    for job in jobs:
        link  = job.get("link", "").strip()
        title = job.get("title", "").strip()

        if not link or not title:
            continue

        # Already notified?
        cur.execute("SELECT 1 FROM seen WHERE link = ?", (link,))
        if cur.fetchone():
            duplicate += 1
            continue

        # Hard block — senior/management
        if _is_blocked(title):
            blocked += 1
            cur.execute(
                "INSERT OR IGNORE INTO seen (link, title, source) VALUES (?, ?, ?)",
                (link, title, job.get("source", ""))
            )
            continue

        # Relevance check — must match at least one tech or role keyword
        if not _is_relevant(title):
            irrelevant += 1
            continue

        # Passed — compute bonus score for sorting
        job["score"] = _bonus(title)

        cur.execute(
            "INSERT OR IGNORE INTO seen (link, title, source) VALUES (?, ?, ?)",
            (link, title, job.get("source", ""))
        )
        passed.append(job)

    con.commit()
    con.close()

    # Sort: highest bonus first
    passed.sort(key=lambda j: -j.get("score", 0))

    print(
        f"[Filter] {len(jobs)} raw → "
        f"{len(passed)} kept | "
        f"{blocked} blocked (senior) | "
        f"{irrelevant} irrelevant | "
        f"{duplicate} already seen"
    )
    return passed