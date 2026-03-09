import re
from collections import Counter

# Pre-defined skill categories for strength chart
SKILL_CATEGORIES = {
    "Frontend": ["react", "javascript", "html", "css", "vue", "angular", "typescript", "figma"],
    "Backend": ["python", "node", "java", "c++", "ruby", "go", "php", "django", "flask", "spring"],
    "Databases": ["sql", "mysql", "mongodb", "postgresql", "redis", "oracle", "nosql"],
    "Machine Learning": ["machine learning", "tensorflow", "pytorch", "scikit-learn", "keras", "pandas", "numpy", "ai"],
    "DevOps/Cloud": ["aws", "docker", "kubernetes", "gcp", "azure", "ci/cd", "linux", "git", "github"]
}

# Pre-defined roles for prediction modeling
ROLES_MAP = {
    "Frontend Developer": ["react", "javascript", "html", "css", "typescript", "vue", "frontend"],
    "Backend Developer": ["python", "java", "node", "sql", "django", "flask", "go", "backend", "api"],
    "Full Stack Developer": ["react", "javascript", "python", "node", "sql", "aws", "docker"],
    "Data Scientist / ML Engineer": ["python", "machine learning", "pandas", "numpy", "sql", "tensorflow", "pytorch"],
    "DevOps Engineer": ["aws", "docker", "kubernetes", "ci/cd", "linux", "python"]
}

def analyze_career_metrics(text_lower, extracted_skills):
    extracted_lower = [s.lower() for s in extracted_skills]
    
    # 1. Skill Categories Strength (0-100 per category)
    skill_strength = {}
    for cat, cat_skills in SKILL_CATEGORIES.items():
        overlap = set(extracted_lower).intersection(cat_skills)
        # Cap score at 100
        score = min(len(overlap) * 20, 100) 
        skill_strength[cat] = score
        
    # 2. Keyword Density (top 10 skills)
    # Using regex to count full word matches of the extracted skills
    keyword_density = []
    for skill in extracted_lower:
        count = len(re.findall(rf'\b{re.escape(skill)}\b', text_lower))
        if count > 0:
            keyword_density.append({"skill": skill.capitalize(), "count": count})
    keyword_density = sorted(keyword_density, key=lambda x: x['count'], reverse=True)[:10]

    # 3. Role Prediction
    role_predictions = []
    for role, role_skills in ROLES_MAP.items():
        overlap = set(extracted_lower).intersection(role_skills)
        if len(role_skills) > 0:
             # Basic naive probability
             prob = min(int((len(overlap) / min(len(role_skills), 5)) * 100), 100)
             if prob > 0:
                 role_predictions.append({"role": role, "match": prob})
    role_predictions = sorted(role_predictions, key=lambda x: x['match'], reverse=True)[:3]

    # 4. Resume Completeness
    sections = {
        "Contact Info": [r'@', r'\b[0-9]{10}\b'],
        "Skills": [r'\bskills\b', r'\btechnologies\b'],
        "Projects": [r'\bprojects\b', r'\bpersonal projects\b'],
        "Experience": [r'\bwork experience\b', r'\bexperience\b', r'\bemployment\b'],
        "Education": [r'\beducation\b', r'\bacademic\b', r'\buniversity\b'],
        "Certifications": [r'\bcertifications\b', r'\bcertificate\b'],
        "Achievements": [r'\bachievements\b', r'\bawards\b']
    }
    
    completeness = []
    for section, patterns in sections.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found = True
                break
        completeness.append({"section": section, "present": found})

    return {
        "skill_strength": skill_strength,
        "keyword_density": keyword_density,
        "role_predictions": role_predictions,
        "completeness": completeness
    }


def calculate_ats_score(text, extracted_skills):
    """
    Calculates an ATS score between 0 and 100 based on the resume text 
    and extracted skills. Returns both the score and deep career metrics.
    """
    score = 0
    text_lower = text.lower()
    
    # 1. Skills Density (Max 40 points)
    num_skills = len(extracted_skills)
    skill_score = min((num_skills / 10) * 40, 40)
    score += skill_score
    
    # 2. Structural Completeness (Max 30 points)
    structure_score = 0
    sections = {
        "experience": [r'\bwork experience\b', r'\bexperience\b', r'\bemployment\b'],
        "education": [r'\beducation\b', r'\bacademic\b', r'\buniversity\b'],
        "projects": [r'\bprojects\b', r'\bpersonal projects\b']
    }
    
    for section, patterns in sections.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found = True
                break
        if found:
            structure_score += 10
            
    score += structure_score
    
    # 3. Measurable Metrics (Max 30 points)
    metrics_pattern = r'\b\d+%\b|\$\d+[kmbKMB]?|\b\d+\b'
    matches = re.findall(metrics_pattern, text)
    metric_score = min((len(matches) / 5) * 30, 30)
    score += metric_score
    
    # Calculate the new career metrics
    career_metrics = analyze_career_metrics(text_lower, extracted_skills)
    
    return int(score), career_metrics
