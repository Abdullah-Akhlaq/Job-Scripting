# scrapers/linkedin.py
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de-DE;q=0.8",
}

# Priority keywords for job titles (higher priority = listed first)
PRIORITY_KEYWORDS = {
    "werkstudent software developer": 1,
    "werkstudent frontend developer": 1,
    "werkstudent backend developer": 1,
    "werkstudent it": 2,
    "internship it": 2,
    "internship software": 2,
    "working student software": 3,
    "working student it": 3,
    "student developer": 3,
}

# Keywords that indicate English language job
ENGLISH_INDICATORS = [
    "english", "english required", "fluent english", 
    "english speaking", "english language",
    "proficient english", "advanced english"
]

# Keywords that indicate Werkstudent/Student role
STUDENT_KEYWORDS = [
    "werkstudent", "working student", "student assistant",
    "internship", "intern", "praktikum", "hiwi"
]

# Job categories we're interested in
JOB_CATEGORIES = [
    "software", "developer", "frontend", "backend", "full-stack",
    "it", "it support", "system", "administrator", "devops",
    "python", "javascript", "java", "c++", "react", "node",
    "database", "sql", "web development", "programming"
]

def is_english_job(text):
    """
    Check if job description/title contains English language indicators.
    Returns True if English is detected, False otherwise.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check for explicit English indicators
    for indicator in ENGLISH_INDICATORS:
        if indicator in text_lower:
            return True
    
    # If no explicit indicator, assume English if text is in English
    # (This is a simple heuristic - if it contains common English words/patterns)
    english_patterns = [
        r"\byou\b", r"\byour\b", r"\bwe\b", r"\bour\b", 
        r"\brequired\b", r"\bpreferred\b", r"\bresponsibilities\b",
        r"\bsalary\b", r"\bbenefits\b"
    ]
    
    for pattern in english_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def is_student_role(text):
    """
    Check if job is explicitly marked as Werkstudent/Internship/Working Student.
    """
    if not text:
        return False
    
    text_lower = text.lower()
    for keyword in STUDENT_KEYWORDS:
        if keyword in text_lower:
            return True
    
    return False

def get_job_priority(title):
    """
    Calculate priority score for job based on keywords.
    Lower number = higher priority (appears first).
    """
    title_lower = title.lower()
    
    for keyword, priority in PRIORITY_KEYWORDS.items():
        if keyword in title_lower:
            return priority
    
    # Check if it matches job category
    for category in JOB_CATEGORIES:
        if category in title_lower:
            return 4  # Medium-low priority for generic IT/Software roles
    
    return 5  # Lowest priority for non-matching roles

def scrape_job_description(job_url):
    """
    Scrape the full job description from the LinkedIn job page.
    Returns the description text or None if scraping fails.
    """
    try:
        resp = requests.get(job_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Try to find job description
        description_div = soup.find("div", class_="show-more-less-html__markup")
        if description_div:
            return description_div.get_text(strip=True)
        
        # Alternative selectors
        desc = soup.find("div", class_="description__text")
        if desc:
            return desc.get_text(strip=True)
        
        return None
    except Exception as e:
        print(f"[LinkedIn] Error scraping job description: {e}")
        return None

def should_include_job(job):
    """
    Determine if a job should be included based on our criteria:
    - Must be in English
    - Must be a Werkstudent/Internship/Working Student role
    - Should be in IT/Software/Administration
    """
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    combined_text = f"{title} {description}"
    
    # Check if it's in English
    if not is_english_job(combined_text):
        return False
    
    # Check if it's a student role
    if not is_student_role(combined_text):
        return False
    
    # Check if it matches our job categories
    has_matching_category = any(
        category in combined_text 
        for category in JOB_CATEGORIES
    )
    
    return has_matching_category

def fetch():
    """
    Fetch jobs from LinkedIn with enhanced filtering.
    """
    jobs = []
    
    # Enhanced search queries
    SEARCHES = [
        "werkstudent software developer Munich",
        "werkstudent frontend developer Munich",
        "werkstudent backend developer Munich",
        "werkstudent IT Munich",
        "internship IT Munich",
        "internship software Munich",
        "working student developer Munich",
        "student IT support Munich",
    ]
    
    for query in SEARCHES:
        url = (
            "https://www.linkedin.com/jobs/search/"
            f"?keywords={query.replace(' ', '%20')}"
            "&location=Munich%2C%20Bavaria%2C%20Germany"
            "&f_TPR=r86400"    # posted in last 24 hours
            "&f_JT=P"          # P = part-time (Werkstudent/Internship)
            "&start=0"
        )
        
        try:
            print(f"[LinkedIn] Fetching: {query}")
            resp = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            cards = soup.find_all("div", class_="base-card")
            
            for card in cards:
                try:
                    title_el   = card.find("h3", class_="base-search-card__title")
                    company_el = card.find("h4", class_="base-search-card__subtitle")
                    location_el= card.find("span", class_="job-search-card__location")
                    date_el    = card.find("time")
                    link_el    = card.find("a", class_="base-card__full-link")

                    if title_el and link_el:
                        job_url = link_el.get("href", "").split("?")[0]
                        
                        # Scrape job description
                        print(f"[LinkedIn] Scraping description for: {title_el.get_text(strip=True)[:50]}...")
                        description = scrape_job_description(job_url)
                        time.sleep(1)  # Be polite
                        
                        job = {
                            "title":       title_el.get_text(strip=True),
                            "company":     company_el.get_text(strip=True) if company_el else "Unknown",
                            "location":    location_el.get_text(strip=True) if location_el else "München",
                            "date":        date_el.get("datetime", "") if date_el else "",
                            "link":        job_url,
                            "description": description or "",
                            "source":      "LinkedIn",
                            "priority":    0,  # Will be set after filtering
                        }
                        
                        # Filter based on our criteria
                        if should_include_job(job):
                            job["priority"] = get_job_priority(job["title"])
                            jobs.append(job)
                            print(f"[LinkedIn] ✓ Added: {job['title']}")
                        else:
                            print(f"[LinkedIn] ✗ Filtered out: {title_el.get_text(strip=True)}")
                
                except Exception as e:
                    print(f"[LinkedIn] Error processing card: {e}")
                    continue

            print(f"[LinkedIn] '{query}': {len(cards)} cards found, {len([j for j in jobs if j['source'] == 'LinkedIn'])} passed filters")
            time.sleep(2)   # be polite — 2 second delay between queries

        except Exception as e:
            print(f"[LinkedIn] ERROR for '{query}': {e}")
    
    # Sort by priority (lower number = higher priority)
    jobs.sort(key=lambda x: x["priority"])
    
    print(f"[LinkedIn] Final count: {len(jobs)} jobs passed all filters")
    return jobs