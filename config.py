import os
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# API Keys - Loaded from environment variables for security
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Resume Folders
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
LOCAL_RESUME_FOLDER = os.path.join(DATA_FOLDER, 'CVs')
RESUME_FOLDER = os.path.join(DATA_FOLDER, 'resume', 'Resumes')
UPLOADED_RESUME_FOLDER = os.path.join(DATA_FOLDER, 'uploads')

# CSV File Path
CSV_FILE_PATH = os.path.join(DATA_FOLDER, 'resumes.csv')
RESUME_CSV_FILE_PATH = os.path.join(DATA_FOLDER, 'resume_Resumes_resumes.csv')


CRITERIA_DEFINITIONS = {
    "total_score": "Overall score based on all criteria (0-100)",
    "experience_score": "Years of relevant work experience in AI/ML and related fields (0-30)",
    "skills_score": "Technical skills match with the job description (0-30)",
    "education_score": "Relevance and level of educational background (0-20)",
    "projects_score": "Quality and relevance of completed projects (0-10)",
    "communication_score": "Resume clarity, professionalism, and effectiveness (0-10)"
}

JOB_DESCRIPTION = "Looking for a Python Developer with AI/ML experience, knowledge of cloud computing, and strong problem-solving skills."