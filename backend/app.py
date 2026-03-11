from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import datetime
import logging

from database import init_db, get_db
from bson.objectid import ObjectId
from resume_parser import parse_resume
from skill_extractor import extract_skills
from ats_scoring import calculate_ats_score, analyze_career_metrics
from job_matcher import match_job_description

app = Flask(__name__)
CORS(app) # Allow cross-origin requests from React

# Configuration
# Read upload folder from environment or default to local uploads/
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set 16MB max limit for secure file handling
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize DB on start
init_db()

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume_api():
    logger.info("Received request at /analyze-resume")
    if 'resume' not in request.files:
        logger.warning("No resume file provided in request")
        return jsonify({"error": "No resume file provided"}), 400
        
    file = request.files['resume']
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        logger.info(f"File securely saved at {filepath}")
        
        # Process the resume
        parsed_data = parse_resume(filepath)
        if "error" in parsed_data:
            logger.error(f"Error parsing resume: {parsed_data['error']}")
            return jsonify(parsed_data), 500
            
        resume_text = parsed_data["text"]
        found_skills = extract_skills(resume_text)
        ats_score, career_metrics = calculate_ats_score(resume_text, found_skills)
        logger.info("Resume successfully parsed and scored")
        
        # Save to database
        db = get_db()
        email = parsed_data.get("email") or f"unknown_{os.urandom(4).hex()}@example.com"
        name = parsed_data.get("name") or "Unknown"
        
        # Insert a single document into resumes collection as requested
        resume_doc = {
            "name": name,
            "email": email,
            "resume_filename": filename,
            "resume_file_path": filepath,
            "resume_text": resume_text,
            "ai_analysis_result": {
                "ats_score": ats_score,
                "extracted_skills": found_skills,
                "career_metrics": career_metrics,
                "job_match_score": 0,
                "missing_skills": [],
                "suggestions": ["Upload a job description to see job match score and missing skills."]
            },
            "upload_timestamp": datetime.datetime.utcnow()
        }
        
        result = db.resumes.insert_one(resume_doc)
        resume_id = str(result.inserted_id)
        logger.info(f"Record stored in MongoDB Atlas with ID: {resume_id}")

        # Cleanup
        # The PDF file is retained on disk in the application as requested
        # Do not delete the file
            
        return jsonify({
            "message": "Resume processed successfully",
            "resume_id": resume_id,
            "parsed_data": parsed_data,
            "skills": found_skills,
            "ats_score": ats_score,
            "career_metrics": career_metrics
        }), 200
        
    logger.warning("Invalid file format uploaded")
    return jsonify({"error": "Invalid file format. Only PDF is supported."}), 400


@app.route('/analyze_job_description', methods=['POST'])
def analyze_job_description_api():
    data = request.json
    resume_id = data.get('resume_id')
    job_description = data.get('job_description')
    
    if not resume_id or not job_description:
        return jsonify({"error": "resume_id and job_description are required"}), 400
        
    db = get_db()
    
    try:
        resume_obj_id = ObjectId(resume_id)
    except:
        return jsonify({"error": "Invalid resume ID format"}), 400
        
    row = db.resumes.find_one({"_id": resume_obj_id})
    
    if not row:
        return jsonify({"error": "Resume not found"}), 404
        
    resume_text = row.get('resume_text', '')
    
    # Calculate match
    match_results = match_job_description(resume_text, job_description)
    
    # Update AnalysisResults inside the resume document
    db.resumes.update_one(
        {"_id": resume_obj_id},
        {"$set": {
            "ai_analysis_result.job_match_score": match_results["match_percentage"],
            "ai_analysis_result.missing_skills": match_results["missing_skills"],
            "ai_analysis_result.suggestions": match_results["suggestions"]
        }}
    )
    
    return jsonify({
        "message": "Job description analyzed",
        "match_results": match_results
    }), 200


@app.route('/analysis/<string:resume_id>', methods=['GET'])
def get_analysis_api(resume_id):
    db = get_db()
    
    try:
        resume_obj_id = ObjectId(resume_id)
        resume_row = db.resumes.find_one({"_id": resume_obj_id})
    except:
        resume_row = None
    
    if not resume_row:
        return jsonify({"error": "Resume analysis not found"}), 404
        
    ai_result = resume_row.get("ai_analysis_result", {})
    
    return jsonify({
        "resume_id": resume_id,
        "ats_score": ai_result.get("ats_score", 0),
        "job_match_score": ai_result.get("job_match_score", 0),
        "extracted_skills": ai_result.get("extracted_skills", []),
        "missing_skills": ai_result.get("missing_skills", []),
        "suggestions": ai_result.get("suggestions", []),
        "career_metrics": ai_result.get("career_metrics", {})
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
