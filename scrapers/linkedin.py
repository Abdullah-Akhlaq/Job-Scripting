# scrapers/linkedin.py
"""
STRICT Werkstudent/Internship Job Scraper

FILTERS:
1. MUST be Werkstudent OR Internship OR Working Student (in title/description)
2. MUST be English language (title or description)
3. MUST match role: Frontend, Fullstack, IT, Administration, Software Developer
4. Searches Germany-wide (not just Munich)
5. Excludes full-time roles
"""

import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8",
}

# ==================== STRICT KEYWORDS ====================

# REQUIRED: Job must explicitly have one of these terms
# These identify Werkstudent/Internship/Working Student positions
MANDATORY_STUDENT_KEYWORDS = {
    "werkstudent": "Werkstudent",
    "working student": "Working Student",
    "work-study student": "Work-Study Student",
    "student assistant": "Student Assistant",
    "student employee": "Student Employee",
    "internship": "Internship",
    "intern": "Intern",
    "praktikum": "Praktikum",
    "hiwi": "HiWi",
    "studentische hilfskraft": "Studentische Hilfskraft",
}

# English language indicators (must find at least one in description)
ENGLISH_LANGUAGE_KEYWORDS = [
    "english required", "english language", "english fluent", "fluent english",
    "english speaking", "must speak english", "proficient english", 
    "advanced english", "business english", "strong english",
    "english skills", "english ability"
]

# STRICT ROLE FILTERS - Only these exact roles
ALLOWED_ROLES = {
    "Frontend": ["frontend", "front-end", "react", "vue", "angular", "react native"],
    "Fullstack": ["fullstack", "full-stack", "full stack"],
    "IT": ["it ", "it support", "it admin", "it technician", "it specialist", "system admin", "system administrator"],
    "Software Developer": ["software developer", "software engineer", "developer", "programmer"],
    "Administration": ["administrator", "admin", "it administration"],
}

# Blacklist words that indicate full-time roles
FULLTIME_BLACKLIST = [
    "full-time", "full time", "fulltime", "full-timer",
    "permanent position", "festanstellung", "unbefristet",
    "40 hours", "40h", "40-hour",
]

# Words to EXCLUDE (indicates role is not suitable)
EXCLUDE_KEYWORDS = [
    "full time", "full-time", "permanent", "festanstellung",
    "senior", "principal", "lead", "manager", "lead developer",
    "sales", "marketing", "business development",
]


def is_mandatory_student_role(text):
    """
    STRICT CHECK: Job title or description MUST contain student/internship keywords.
    Returns: True if found, False otherwise
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    for keyword in MANDATORY_STUDENT_KEYWORDS.keys():
        if keyword in text_lower:
            print(f"[LinkedIn Filter] ✓ Found student role keyword: '{keyword}'")
            return True
    
    print(f"[LinkedIn Filter] ✗ No Werkstudent/Internship keywords found")
    return False


def is_english_language(text):
    """
    STRICT CHECK: Description must contain English language indicators.
    Returns: True if English is detected, False otherwise
    """
    if not text:
        print(f"[LinkedIn Filter] ✗ No text to check for English")
        return False
    
    text_lower = text.lower()
    
    # Check for explicit English language requirement
    for keyword in ENGLISH_LANGUAGE_KEYWORDS:
        if keyword in text_lower:
            print(f"[LinkedIn Filter] ✓ Found English indicator: '{keyword}'")
            return True
    
    # Check for common English patterns in job description
    english_patterns = [
        r"\byou\b", r"\byour\b", r"\bwe\b", r"\bour\b",
        r"\bresponsibilities\b", r"\brequirements\b",
        r"\bwill\b", r"\bwould\b", r"\bshould\b",
    ]
    
    english_count = 0
    for pattern in english_patterns:
        if re.search(pattern, text_lower):
            english_count += 1
    
    if english_count >= 3:
        print(f"[LinkedIn Filter] ✓ Detected English language (pattern match: {english_count} patterns)")
        return True
    
    print(f"[LinkedIn Filter] ✗ Description does not appear to be in English")
    return False


def matches_allowed_role(text):
    """
    STRICT CHECK: Job must match one of the allowed roles.
    Returns: Role name if matched, None otherwise
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    for role_name, keywords in ALLOWED_ROLES.items():
        for keyword in keywords:
            if keyword in text_lower:
                print(f"[LinkedIn Filter] ✓ Matched role: {role_name} (keyword: '{keyword}')")
                return role_name
    
    print(f"[LinkedIn Filter] ✗ Does not match allowed roles (Frontend/Fullstack/IT/Admin/Software Dev)")
    return None


def is_not_fulltime(text):
    """
    STRICT CHECK: Job should NOT be full-time.
    Returns: True if not full-time, False if it appears to be full-time
    """
    if not text:
        return True
    
    text_lower = text.lower()
    
    # Check for full-time indicators
    for blacklist_word in FULLTIME_BLACKLIST:
        if blacklist_word in text_lower:
            print(f"[LinkedIn Filter] ✗ Detected full-time role: '{blacklist_word}'")
            return False
    
    print(f"[LinkedIn Filter] ✓ Not detected as full-time")
    return True


def should_exclude_job(text):
    """
    Check if job has ANY exclusion keywords.
    Returns: True if should exclude, False if OK to include
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    for exclude_word in EXCLUDE_KEYWORDS:
        if exclude_word in text_lower:
            print(f"[LinkedIn Filter] ✗ Excluded: contains '{exclude_word}'")
            return True
    
    return False


def scrape_job_description(job_url):
    """
    Scrape the full job description from LinkedIn job page.
    Returns: description text or empty string if fails
    """
    try:
        resp = requests.get(job_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try primary selector
        description_div = soup.find("div", class_="show-more-less-html__markup")
        if description_div:
            return description_div.get_text(strip=True)
        
        # Try alternative selectors
        desc = soup.find("div", class_="description__text")
        if desc:
            return desc.get_text(strip=True)
        
        return ""
    except Exception as e:
        print(f"[LinkedIn] Error scraping job description: {e}")
        return ""


def get_job_priority(title, role):
    """
    All Werkstudent roles = priority 1 (high)
    All Internship roles = priority 2 (medium)
    Returns: priority score (lower = higher priority)
    """
    title_lower = title.lower()
    
    # Werkstudent gets highest priority
    if "werkstudent" in title_lower or "working student" in title_lower:
        return 1
    
    # Internship gets medium priority
    if "intern" in title_lower or "praktikum" in title_lower:
        return 2
    
    # Default
    return 2


def filter_job(job):
    """
    Apply ALL STRICT filters to a job.
    Returns: (include: bool, role_name: str or None, reason: str)
    """
    title = job.get("title", "")
    description = job.get("description", "")
    combined = f"{title} {description}"
    
    print(f"\n[LinkedIn Filter] Checking: {title[:60]}...")
    
    # Filter 1: MUST be Werkstudent/Internship
    if not is_mandatory_student_role(combined):
        return False, None, "Not a Werkstudent/Internship role"
    
    # Filter 2: MUST NOT be full-time
    if not is_not_fulltime(combined):
        return False, None, "Appears to be full-time position"
    
    # Filter 3: MUST match allowed role
    matched_role = matches_allowed_role(combined)
    if not matched_role:
        return False, None, "Does not match allowed roles"
    
    # Filter 4: MUST be in English
    if not is_english_language(description):
        return False, matched_role, "Description is not in English"
    
    # Filter 5: Should NOT have exclusion keywords
    if should_exclude_job(combined):
        return False, matched_role, "Contains exclusion keywords"
    
    print(f"[LinkedIn Filter] ✓✓✓ PASSED ALL FILTERS - {matched_role} role ✓✓✓")
    return True, matched_role, "Passed all filters"


def fetch():
    """
    Fetch ONLY Werkstudent/Internship jobs from LinkedIn.
    STRICT filtering for student roles in Germany.
    """
    jobs = []
    
    # Germany-wide searches (not just Munich)
    SEARCHES = [
        "werkstudent frontend developer Germany",
        "werkstudent fullstack developer Germany",
        "werkstudent software developer Germany",
        "werkstudent it support Germany",
        "werkstudent it administrator Germany",
        "internship frontend developer Germany",
        "internship fullstack developer Germany",
        "internship software developer Germany",
        "internship it Germany",
        "working student developer Germany",
    ]
    
    for query in SEARCHES:
        url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={query.replace(' ', '%20')}"
            "&location=Germany"
            "&f_TPR=r86400"    # posted in last 24 hours
            "&f_JT=P"          # P = part-time (Werkstudent/Internship)
            "&start=0"
        )
        
        try:
            print(f"\n[LinkedIn] Searching: {query}")
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.find_all("div", class_="base-card")
            print(f"[LinkedIn] Found {len(cards)} job cards")
            
            for card in cards:
                try:
                    title_el   = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el= card.find("span", class_="job-search-card__location")
                    date_el    = card.find("time")
                    link_el    = card.find("a", class_="base-card__full-link")

                    if not (title_el and link_el):
                        continue

                    job_url = link_el.get("href", "").split("?")[0]
                    
                    # Scrape full description
                    print(f"[LinkedIn] Scraping: {title_el.get_text(strip=True)[:50]}...")
                    description = scrape_job_description(job_url)
                    time.sleep(1)  # Be polite to LinkedIn
                    
                    job = {
                        "title":       title_el.get_text(strip=True),
                        "company":     company_el.get_text(strip=True) if company_el else "Unknown",
                        "location":    location_el.get_text(strip=True) if location_el else "Germany",
                        "date":        date_el.get("datetime", "") if date_el else "",
                        "link":        job_url,
                        "description": description,
                        "source":      "LinkedIn",
                        "priority":    5,  # Will be updated if job passes filters
                    }
                    
                    # Apply STRICT filters
                    include, role, reason = filter_job(job)
                    
                    if include:
                        job["role"] = role
                        job["priority"] = get_job_priority(job["title"], role)
                        jobs.append(job)
                        print(f"[LinkedIn] ✅ ADDED: {job['title']}")
                    else:
                        print(f"[LinkedIn] ❌ REJECTED: {reason}")
                
                except Exception as e:
                    print(f"[LinkedIn] Error processing job: {e}")
                    continue

            time.sleep(2)   # Be polite — delay between queries

        except Exception as e:
            print(f"[LinkedIn] ERROR fetching '{query}': {e}")
    
    # Sort by priority (lower = higher priority)
    jobs.sort(key=lambda x: x["priority"])
    
    print(f"\n{'='*60}")
    print(f"[LinkedIn] FINAL RESULT: {len(jobs)} Werkstudent/Internship jobs found")
    print(f"{'='*60}")
    
    return jobs