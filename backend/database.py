from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Use MongoDB URI from environment or fallback to localhost
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://raghavkakrania5_db_user:X07sOFfNMnrNi97y@cluster0.pvwprfq.mongodb.net/resume_analyzer?retryWrites=true&w=majority&appName=Cluster0')

def get_db():
    client = MongoClient(MONGO_URI)
    # Using 'resume_analyzer' as the default database name
    db = client["resume_analyzer"]
    return db

def init_db():
    # MongoDB creates databases and collections lazily.
    # We can create indexes here if needed.
    db = get_db()
    # Create unique index on email for Users
    db.Users.create_index("email", unique=True)
    pass

if __name__ == '__main__':
    init_db()
    print("Database connection and indexes initialized.")
