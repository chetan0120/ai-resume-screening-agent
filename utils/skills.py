import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy of skills categorised by domain
SKILLS_TAXONOMY = {
    "languages": [
        "Python", "JavaScript", "TypeScript", "Java", "C\\+\\+", "C#", "C", "Go", "Golang", 
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Objective-C", "SQL", "HTML", "CSS", 
        "Sass", "Scala", "R", "MATLAB", "Perl", "Bash", "Shell", "PowerShell", "Dart"
    ],
    "frameworks": [
        "React", "Angular", "Vue", "Vue\\.js", "Svelte", "Next\\.js", "Nuxt\\.js", "Express", 
        "Express\\.js", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel", "Ruby on Rails", 
        "ASP\\.NET", "NestJS", "Symfony", "Play Framework", "Gatsby", "TailwindCSS", "Bootstrap"
    ],
    "databases": [
        "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite", "DynamoDB", "Cassandra", 
        "MariaDB", "Oracle", "Microsoft SQL Server", "SQL Server", "Elasticsearch", 
        "Firebase", "Firestore", "Neo4j", "InfluxDB"
    ],
    "cloud_devops": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Google Cloud Platform", 
        "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Jenkins", "GitHub Actions", 
        "GitLab CI", "CI/CD", "CircleCI", "Nginx", "Apache", "Prometheus", "Grafana", 
        "Serverless", "Cloudflare"
    ],
    "libraries_tools": [
        "Git", "Jira", "Confluence", "Postman", "Linux", "Webpack", "Vite", "Babel", 
        "Pandas", "NumPy", "SciPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras", 
        "OpenCV", "NLTK", "Spacy", "Hugging Face", "Matplotlib", "Seaborn", "Redux", 
        "GraphQL", "REST API", "gRPC", "WebSockets", "Docker Compose"
    ],
    "soft_skills": [
        "Communication", "Leadership", "Teamwork", "Collaboration", "Problem Solving", 
        "Critical Thinking", "Adaptability", "Creativity", "Time Management", 
        "Conflict Resolution", "Agile", "Scrum", "Project Management", "Mentoring", 
        "Public Speaking", "Negotiation", "Emotional Intelligence", "Decision Making",
        "Active Listening", "Work Ethic", "Interpersonal Skills"
    ]
}

def extract_skills(text: str) -> Dict[str, List[str]]:
    """
    Extract skills from the provided text using regex patterns from the taxonomy.
    Matches are case-insensitive and enforce word boundaries.
    
    Args:
        text (str): Input text (resume or job description).
        
    Returns:
        Dict[str, List[str]]: Dictionary with skill categories as keys and list of matched skills.
    """
    extracted = {}
    if not text:
        return {cat: [] for cat in SKILLS_TAXONOMY.keys()}
        
    for category, skill_list in SKILLS_TAXONOMY.items():
        matched_skills = set()
        for skill in skill_list:
            # We escape skills but the taxonomy already contains double backslashes where needed.
            # Handle special characters like C++ and C# carefully.
            # We want to match word boundaries, but note that \b doesn't work perfectly on trailing '+' or '#'.
            # So we use a custom boundary check.
            if skill in ["C\\+\\+", "C#", "F#"]:
                # Custom boundary matching for C++ and C#
                pattern = r'(?:^|[\s,;:\(\)\{\}\[\]])(' + skill + r')(?:$|[\s,;:\(\)\{\}\[\]\.\?!])'
            else:
                pattern = r'\b' + skill + r'\b'
                
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Normalize representation (e.g. C\\+\\+ -> C++, Vue\\.js -> Vue.js)
                display_name = skill.replace("\\+", "+").replace("\\.", ".")
                # Also clean Go vs Golang redundancy, AWS vs Amazon Web Services, GCP vs Google Cloud
                matched_skills.add(display_name)
                
        extracted[category] = sorted(list(matched_skills))
        
    return extracted

def analyze_skills_overlap(resume_text: str, jd_text: str) -> Tuple[Dict[str, List[str]], Dict[str, List[str]], List[str], List[str]]:
    """
    Analyzes skills in both resume and JD, separating found skills and missing skills.
    
    Args:
        resume_text (str): Extracted resume text.
        jd_text (str): Job description text.
        
    Returns:
        Tuple:
            - Dict: Skills found in resume (categorized)
            - Dict: Skills required by JD but missing in resume (categorized)
            - List: Flat list of all found skills
            - List: Flat list of all missing skills
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    
    found_skills_categorized = {}
    missing_skills_categorized = {}
    
    all_found = set()
    all_missing = set()
    
    for category in SKILLS_TAXONOMY.keys():
        r_skills = set(resume_skills[category])
        j_skills = set(jd_skills[category])
        
        # Found are skills present in the resume that might also be required by the JD
        # We can define "found_skills" as all skills present in the resume.
        found_skills_categorized[category] = sorted(list(r_skills))
        
        # Missing are skills present in the JD but not in the resume
        missing = j_skills - r_skills
        missing_skills_categorized[category] = sorted(list(missing))
        
        # Aggregate
        all_found.update(r_skills)
        all_missing.update(missing)
        
    # Flat lists
    flat_found = sorted(list(all_found))
    flat_missing = sorted(list(all_missing))
    
    return found_skills_categorized, missing_skills_categorized, flat_found, flat_missing
