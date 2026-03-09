import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'database.db')

def get_db_connection():
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE
        )
    ''')
    
    # Create Resumes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            resume_text TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
    ''')
    
    # Create Skills Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            skill_name TEXT,
            FOREIGN KEY (resume_id) REFERENCES Resumes(id)
        )
    ''')
    
    # Create AnalysisResults Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AnalysisResults (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER,
            ats_score INTEGER,
            job_match_score INTEGER,
            missing_skills TEXT,
            suggestions TEXT,
            FOREIGN KEY (resume_id) REFERENCES Resumes(id)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
