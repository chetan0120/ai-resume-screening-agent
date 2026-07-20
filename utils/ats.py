import re
from typing import Dict, List, Any

def analyze_ats_compliance(resume_text: str, jd_text: str, found_skills: List[str], missing_skills: List[str]) -> Dict[str, Any]:
    """
    Computes an ATS score and analyzes formatting, section presence, and keyword coverage.
    
    Args:
        resume_text (str): Cleaned resume text.
        jd_text (str): Job description text.
        found_skills (List[str]): List of skills found.
        missing_skills (List[str]): List of required skills missing.
        
    Returns:
        Dict[str, Any]: ATS report dictionary containing the score and detailed audits.
    """
    scorecard = {
        "ats_score": 0.0,
        "sections_found": {
            "experience": False,
            "education": False,
            "skills": False,
            "contact": False
        },
        "contact_info": {
            "email_found": False,
            "phone_found": False,
            "linkedin_found": False
        },
        "formatting_issues": [],
        "keyword_coverage": 0.0,
        "word_count": 0
    }
    
    if not resume_text:
        return scorecard

    text_lower = resume_text.lower()
    
    # 1. Section presence checks using common variations of section titles
    experience_patterns = [r'\bwork\b', r'\bexperience\b', r'\bemployment\b', r'\bhistory\b', r'\bcareer\b', r'\bprofessional\b']
    education_patterns = [r'\beducation\b', r'\bacademics\b', r'\bdegree\b', r'\buniversity\b', r'\bcollege\b']
    skills_patterns = [r'\bskills\b', r'\btechnologies\b', r'\btech stack\b', r'\bcompetencies\b', r'\bexpertise\b']
    contact_patterns = [r'\bcontact\b', r'\bemail\b', r'\bphone\b', r'\blinkedin\b', r'\baddress\b']
    
    scorecard["sections_found"]["experience"] = any(re.search(pat, text_lower) for pat in experience_patterns)
    scorecard["sections_found"]["education"] = any(re.search(pat, text_lower) for pat in education_patterns)
    scorecard["sections_found"]["skills"] = any(re.search(pat, text_lower) for pat in skills_patterns)
    scorecard["sections_found"]["contact"] = any(re.search(pat, text_lower) for pat in contact_patterns)
    
    # 2. Contact details validation
    email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    linkedin_regex = r'linkedin\.com\/in\/[a-zA-Z0-9_-]+'
    
    emails = re.findall(email_regex, resume_text)
    phones = re.findall(phone_regex, resume_text)
    linkedins = re.findall(linkedin_regex, text_lower)
    
    scorecard["contact_info"]["email_found"] = len(emails) > 0
    scorecard["contact_info"]["phone_found"] = len(phones) > 0
    scorecard["contact_info"]["linkedin_found"] = len(linkedins) > 0
    
    # 3. Formatting issues and analysis
    # Word count checking
    word_count = len(resume_text.split())
    scorecard["word_count"] = word_count
    
    if word_count < 100:
        scorecard["formatting_issues"].append("Resume is too short (under 100 words). Add more detail about your achievements.")
    elif word_count > 1500:
        scorecard["formatting_issues"].append("Resume is extremely long (over 1500 words). Try to condense it to 1-2 pages.")
        
    if not scorecard["contact_info"]["email_found"]:
        scorecard["formatting_issues"].append("Missing contact email. Recruiters need a clear way to contact you.")
    if not scorecard["contact_info"]["phone_found"]:
        scorecard["formatting_issues"].append("Missing contact phone number. Add a phone number to improve contactability.")
    if not scorecard["contact_info"]["linkedin_found"]:
        scorecard["formatting_issues"].append("No LinkedIn profile detected. Modern professional resumes benefit from a LinkedIn link.")
        
    for section, found in scorecard["sections_found"].items():
        if not found:
            scorecard["formatting_issues"].append(f"Could not reliably locate the '{section.capitalize()}' section header. Standardize your headings.")

    # 4. Keyword Coverage
    # Let's assess skill/keyword coverage based on JD requirements
    total_required = len(found_skills) + len(missing_skills)
    if total_required > 0:
        coverage = (len(found_skills) / total_required) * 100.0
        scorecard["keyword_coverage"] = round(coverage, 2)
    else:
        # If JD has no extracted skills, default coverage based on a standard subset
        scorecard["keyword_coverage"] = 100.0
        
    # 5. Composite ATS Score Calculation
    # Weights: Keyword Coverage (40%), Section Presence (30%), Contact Information (20%), Formatting Heuristics (10%)
    
    # Section Presence score (0 to 30)
    section_score = sum(10 for s in scorecard["sections_found"].values() if s)
    section_score = min(30, section_score * (30/4)) # scaling
    
    # Contact Info score (0 to 20)
    contact_score = sum(10 for c in scorecard["contact_info"].values() if c)
    contact_score = min(20, contact_score * (20/3)) # scaling
    
    # Keyword Coverage score (0 to 40)
    keyword_score = scorecard["keyword_coverage"] * 0.40
    
    # Formatting score (0 to 10)
    issues_count = len(scorecard["formatting_issues"])
    formatting_score = max(0, 10 - (issues_count * 2))
    
    # Total Score
    total_ats_score = round(section_score + contact_score + keyword_score + formatting_score, 2)
    scorecard["ats_score"] = max(0.0, min(100.0, total_ats_score))
    
    return scorecard
