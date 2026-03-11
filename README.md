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

## 🚀 Deployment Instructions (Railway)

This project is a monorepo containing both the frontend and backend. You can deploy both as separate services within a single **Railway** project.

### Step 1: Deploy the Backend
1. In your [Railway](https://railway.app) dashboard, click **New Project** -> **Deploy from GitHub repo** and select your repository.
2. Once added, go to the Service's **Settings > General** and change the **Root Directory** to `/backend`.
3. Go to **Variables** and add your MongoDB connection string:
   ```bash
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.../resume_analyzer?...
   ```
4. Wait for the build to finish. Railway will use the `/backend/Procfile` to automatically download the required SpaCy NLP model and start the `gunicorn` server securely.
5. Go to **Settings > Domains** and click **Generate Domain** (e.g., `your-backend.up.railway.app`). Copy this URL.

### Step 2: Deploy the Frontend
1. In the **same Railway project**, click **New** -> **GitHub Repo** and select the exact same repository again (this creates a second service).
2. Go to the new frontend Service's **Settings > General** and change the **Root Directory** to `/frontend`.
3. Go to **Variables** and add the API URL pointing to the backend domain you just generated in Step 1:
   ```bash
   REACT_APP_API_URL=https://your-backend.up.railway.app
   ```
4. Wait for the build to finish. Railway will detect your React app, build it, and serve it automatically.
5. Go to **Settings > Domains** and click **Generate Domain**. **This is your live website URL!**

---

## 💻 Local Setup (Development)

If you wish to test the application locally:

### 1. Backend Setup

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
