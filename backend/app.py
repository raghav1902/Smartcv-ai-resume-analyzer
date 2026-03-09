from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

from database import init_db, get_db_connection
from resume_parser import parse_resume
from skill_extractor import extract_skills
from ats_scoring import calculate_ats_score, analyze_career_metrics
from job_matcher import match_job_description

app = Flask(__name__)
CORS(app) # Allow cross-origin requests from React

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB on start
init_db()

@app.route('/upload_resume', methods=['POST'])
def upload_resume_api():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the resume
        parsed_data = parse_resume(filepath)
        if "error" in parsed_data:
            return jsonify(parsed_data), 500
            
        resume_text = parsed_data["text"]
        found_skills = extract_skills(resume_text)
        ats_score, career_metrics = calculate_ats_score(resume_text, found_skills)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create a dummy user for now if we don't have auth
        cursor.execute("INSERT OR IGNORE INTO Users (name, email) VALUES (?, ?)", 
                       (parsed_data.get("name") or "Unknown", parsed_data.get("email") or f"unknown_{os.urandom(4).hex()}@example.com"))
        conn.commit()
        
        cursor.execute("SELECT id FROM Users WHERE email = ?", (parsed_data.get("email") or f"unknown_{os.urandom(4).hex()}@example.com",))
        user_id_row = cursor.fetchone()
        user_id = user_id_row['id'] if user_id_row else 1 # Fallback to 1
        
        cursor.execute("INSERT INTO Resumes (user_id, resume_text) VALUES (?, ?)", (user_id, resume_text))
        resume_id = cursor.lastrowid
        
        # Store Skills
        for skill in found_skills:
            cursor.execute("INSERT INTO Skills (resume_id, skill_name) VALUES (?, ?)", (resume_id, skill))
            
        # Store Initial Analysis (No job match yet)
        cursor.execute('''
            INSERT INTO AnalysisResults (resume_id, ats_score, job_match_score, missing_skills, suggestions) 
            VALUES (?, ?, ?, ?, ?)
        ''', (resume_id, ats_score, 0, "", "Upload a job description to see job match score and missing skills."))
        
        conn.commit()
        conn.close()
        
        # Cleanup
        try:
            os.remove(filepath)
        except OSError:
            pass
            
        return jsonify({
            "message": "Resume processed successfully",
            "resume_id": resume_id,
            "parsed_data": parsed_data,
            "skills": found_skills,
            "ats_score": ats_score,
            "career_metrics": career_metrics
        }), 200
        
    return jsonify({"error": "Invalid file format. Only PDF is supported."}), 400


@app.route('/analyze_job_description', methods=['POST'])
def analyze_job_description_api():
    data = request.json
    resume_id = data.get('resume_id')
    job_description = data.get('job_description')
    
    if not resume_id or not job_description:
        return jsonify({"error": "resume_id and job_description are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT resume_text FROM Resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"error": "Resume not found"}), 404
        
    resume_text = row['resume_text']
    
    # Calculate match
    match_results = match_job_description(resume_text, job_description)
    
    # Update AnalysisResults
    cursor.execute('''
        UPDATE AnalysisResults 
        SET job_match_score = ?, missing_skills = ?, suggestions = ?
        WHERE resume_id = ?
    ''', (
        match_results["match_percentage"], 
        ",".join(match_results["missing_skills"]), 
        "\\n".join(match_results["suggestions"]),
        resume_id
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Job description analyzed",
        "match_results": match_results
    }), 200


@app.route('/analysis/<int:resume_id>', methods=['GET'])
def get_analysis_api(resume_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT a.ats_score, a.job_match_score, a.missing_skills, a.suggestions, r.resume_text 
        FROM AnalysisResults a
        JOIN Resumes r ON a.resume_id = r.id
        WHERE a.resume_id = ?
    ''', (resume_id,))
    
    analysis_row = cursor.fetchone()
    
    if not analysis_row:
        conn.close()
        return jsonify({"error": "Analysis not found"}), 404
        
    cursor.execute("SELECT skill_name FROM Skills WHERE resume_id = ?", (resume_id,))
    skills_rows = cursor.fetchall()
    skills = [row['skill_name'] for row in skills_rows]
    
    # Calculate deep career metrics dynamically
    career_metrics = analyze_career_metrics(analysis_row['resume_text'].lower(), skills)
    
    return jsonify({
        "resume_id": resume_id,
        "ats_score": analysis_row['ats_score'],
        "job_match_score": analysis_row['job_match_score'],
        "extracted_skills": skills,
        "missing_skills": analysis_row['missing_skills'].split(',') if analysis_row['missing_skills'] else [],
        "suggestions": analysis_row['suggestions'].split('\\n') if analysis_row['suggestions'] else [],
        "career_metrics": career_metrics
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
