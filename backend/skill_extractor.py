import re

# A comprehensive predefined list of technical skills for text matching
TECHNICAL_SKILLS = [
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go",
    "rust", "typescript", "html", "css", "sql", "nosql", "mongodb", "postgresql", "mysql",
    "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "asp.net",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix", "git", "github", "gitlab",
    "ci/cd", "jenkins", "terraform", "machine learning", "deep learning", "nlp", "tensorflow",
    "keras", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn", "tableau",
    "powerbi", "excel", "agile", "scrum", "kanban", "jira", "confluence", "trello",
    "rest api", "graphql", "microservices", "serverless", "oop", "data structures", "algorithms"
]

def extract_skills(text):
    """
    Extracts predefined technical skills from the given text.
    """
    text_lower = text.lower()
    extracted_skills = set()
    
    for skill in TECHNICAL_SKILLS:
        # Use regex border to avoid partial matches (e.g., 'go' in 'good')
        # Handle special characters like C++, Node.js
        escaped_skill = re.escape(skill)
        pattern = r'\b' + escaped_skill + r'\b'
        
        if re.search(pattern, text_lower):
            extracted_skills.add(skill.title())
            
    return list(extracted_skills)
