import os
import glob
from config import LOCAL_RESUME_FOLDER, RESUME_FOLDER

# Function to list all PDF resumes in the local folder
def list_pdfs():
    if not os.path.exists(LOCAL_RESUME_FOLDER):
        print(f"Local resume folder '{LOCAL_RESUME_FOLDER}' not found.")
        return []
    
    pdf_files = []
    for file_path in glob.glob(os.path.join(LOCAL_RESUME_FOLDER, "*.pdf")):
        filename = os.path.basename(file_path)
        file_id = os.path.splitext(filename)[0]  # Use filename without extension as ID
        pdf_files.append({
            "name": filename,
            "id": file_id,
            "path": file_path
        })
    
    return pdf_files

# Function to list all DOCX resumes in the resume folder
def list_docx():
    if not os.path.exists(RESUME_FOLDER):
        print(f"Resume folder '{RESUME_FOLDER}' not found.")
        return []
    
    docx_files = []
    for file_path in glob.glob(os.path.join(RESUME_FOLDER, "*.docx")):
        filename = os.path.basename(file_path)
        file_id = os.path.splitext(filename)[0]  # Use filename without extension as ID
        docx_files.append({
            "name": filename,
            "id": file_id,
            "path": file_path
        })
    
    return docx_files

# Fetch resumes from CVs folder (PDF files)
def fetch_resumes():
    pdf_files = list_pdfs()
    return [{"name": file["name"], "id": file["id"], "path": file["path"]} for file in pdf_files]

# Fetch resumes from resume/Resumes folder (DOCX files)
def fetch_resume_resumes():
    docx_files = list_docx()
    return [{"name": file["name"], "id": file["id"], "path": file["path"]} for file in docx_files]