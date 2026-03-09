import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skill_extractor import extract_skills
from ats_scoring import calculate_ats_score

def match_job_description(resume_text, job_description_text):
    """
    Compares the resume text against the job description using TF-IDF 
    and cosine similarity to generate a match percentage.
    Also identifies missing skills based on the skill extractor.
    """
    # 1. Compute cosine similarity score (Text match Contextual 40%)
    vectorizer = TfidfVectorizer(stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        cosine_score = round(similarity * 100, 2)
    except Exception as e:
        print(f"Error computing similarity: {e}")
        cosine_score = 0.0
        
    # 2. Extract skills to find what's missing and overlap (Keyword Match 40%)
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description_text))
    
    missing_skills = list(job_skills - resume_skills)
    matched_skills = list(job_skills.intersection(resume_skills))
    
    if len(job_skills) > 0:
        skill_overlap_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        skill_overlap_score = 100.0 if len(resume_skills) > 0 else 0.0

    # 3. Base Structural Completeness (20%)
    # Use the existing calculate_ats_score to get the structural baseline
    base_ats_score, _ = calculate_ats_score(resume_text, list(resume_skills))
    
    # 4. Compute Unified Score
    # Weighting: 40% Cosine TFIDF, 40% Keyword Match, 20% Structure
    integrated_match_score = (0.4 * cosine_score) + (0.4 * skill_overlap_score) + (0.2 * base_ats_score)
    integrated_match_score = min(round(integrated_match_score), 100) # Cap at 100
    
    # 5. Provide suggestions
    suggestions = []
    if missing_skills:
        suggestions.append(f"Consider learning or adding these required skills: {', '.join(missing_skills[:5])}")
    
    if integrated_match_score < 50:
        suggestions.append("Tailor your resume more closely to the key responsibilities in the job description using specific keywords.")
    elif integrated_match_score >= 80:
        suggestions.append("Great job! Your resume aligns very well with the job description.")
    else:
        suggestions.append("Good start, but boosting your skill keywords and metrics could bump up your ATS compatibility.")
        
    return {
        "match_percentage": integrated_match_score, # We hijack match_percentage for the new integrated ATS Score
        "cosine_similarity": cosine_score,
        "skill_overlap": round(skill_overlap_score, 1),
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
        "suggestions": suggestions
    }
