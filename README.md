# AI Resume Analyzer with ATS Score & Job Matching

A full-stack web application that allows users to upload their resume (PDF), analyzes the resume using NLP techniques, extracts important skills, calculates an ATS score, compares the resume with a job description, and provides actionable suggestions.

## Features
- **Resume Upload & Parsing:** Drag-and-drop PDF extraction.
- **NLP Skill Extraction:** Identifies technical skills using RegEx and NLP boundaries.
- **ATS Resume Score:** Calculates a 0-100 score based on skill density and structural completeness.
- **Job Description Matching:** Uses TF-IDF and Cosine Similarity to compare your resume against a target job description.
- **Feedback & Analysis:** Provides suggestions on missing skills and missing sections.
- **Modern Dashboard:** Built with React, featuring glassmorphism elements, clean layout, and real-time feedback.

---

## Tech Stack
- **Backend:** Python, Flask, MongoDB, PyPDF2, spaCy, NLTK, scikit-learn, pandas
- **Frontend:** React (Create React App), Axios, Lucide React, React Dropzone

---

## How to Run the Project Locally

### 1. Backend Setup

Open a terminal and navigate to the `backend` folder:
```bash
cd AI-Resume-Analyzer/backend
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
- Windows: `.\\venv\\Scripts\\Activate.ps1`
- Mac/Linux: `source venv/bin/activate`

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

Download the necessary NLP model for spaCy:
```bash
python -m spacy download en_core_web_sm
```

### Configure MongoDB
The application uses MongoDB to store user and resume data.
1. Install MongoDB Locally (or use MongoDB Atlas for a cloud database).
2. Start the MongoDB service on your local machine if not using Atlas. 
3. Setup Environment Variables: By default, the application will try to connect to `mongodb://localhost:27017/`. If you are using MongoDB Atlas or a custom port, create a `.env` file in the `backend` folder and add:
```bash
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
```

Start the Flask REST API server (runs on port 5000):
```bash
python app.py
```

### 2. Frontend Setup

Open a **new** terminal and navigate to the `frontend` folder:
```bash
cd AI-Resume-Analyzer/frontend
```

Start the React development server (runs on port 3000):
```bash
npm start
```

### 3. Usage
- Once both servers are running, access the application in your browser at `http://localhost:3000`.
- Drag and drop your `.pdf` resume onto the dropzone.
- Wait for the NLP analysis to complete.
- Review your ATS Score and extracted skills.
- Paste a sample Job Description into the matching form to see your Match Percentage and Missing Skills output.

---

## Folder Structure Highlights
- `/backend/app.py`: Main Flask API Router. Features the core `/analyze-resume` endpoint.
- `/backend/resume_parser.py`: PDF text and named entity extraction.
- `/backend/ats_scoring.py`: Heuristics logic for generating your overall resume strength score.
- `/backend/job_matcher.py`: TF-IDF scoring against target job description text.
- `/frontend/src/App.js`: Core React Dashboard and Upload state machine.
- `/frontend/src/index.css`: Vanilla CSS Design System with variables and utility classes.
