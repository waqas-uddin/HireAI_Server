import os
import pandas as pd
import PyPDF2
from docx import Document
from drive import fetch_resume_resumes
from rank import score_resume
from config import RESUME_CSV_FILE_PATH, JOB_DESCRIPTION, CRITERIA_DEFINITIONS
import re


# Extract text from a DOCX file
def extract_text(file_path):
    try:
        # Check if it's a DOCX file
        if file_path.endswith('.docx'):
            doc = Document(file_path)
            text = " ".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        # Handle PDF files (for compatibility, though we're only processing DOCX now)
        else:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                return text
    except Exception as e:
        print(f"Error extracting text from file {file_path}: {e}")
        return ""


# Extract only essential information from resume text to reduce API load
def extract_essential_resume_info(resume_text):
    """
    Extract only the most essential information from resume to reduce API load
    Focuses on work experience, skills, education, and projects
    """
    # Convert to lowercase for easier matching
    text_lower = resume_text.lower()
    
    # Define key section identifiers
    experience_keywords = ['experience', 'work', 'employment', 'professional']
    skills_keywords = ['skills', 'technical', 'programming', 'languages', 'tools', 'technologies']
    education_keywords = ['education', 'degree', 'university', 'college', 'academic']
    projects_keywords = ['projects', 'portfolio', 'work samples']
    
    # Split text into lines for easier processing
    lines = resume_text.split('\n')
    
    essential_info = []
    current_section = None
    
    # Look for key sections and extract relevant content
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip empty lines
        if not line_lower:
            continue
            
        # Identify section headers
        if any(keyword in line_lower for keyword in experience_keywords):
            current_section = 'experience'
            essential_info.append(line)
        elif any(keyword in line_lower for keyword in skills_keywords):
            current_section = 'skills'
            essential_info.append(line)
        elif any(keyword in line_lower for keyword in education_keywords):
            current_section = 'education'
            essential_info.append(line)
        elif any(keyword in line_lower for keyword in projects_keywords):
            current_section = 'projects'
            essential_info.append(line)
        # Extract content from identified sections
        elif current_section and len(line.strip()) > 10:
            # Only add substantial lines (more than 10 characters)
            essential_info.append(line)
        # Always include contact information (name, email, phone)
        elif re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line) or re.search(r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})', line):
            essential_info.append(line)
    
    # If no sections found, return first 500 words as fallback
    if not essential_info:
        words = resume_text.split()
        return " ".join(words[:500]) if len(words) > 500 else resume_text
    
    return "\n".join(essential_info[:100])  # Limit to first 100 lines


# Process resumes from resume/Resumes folder (DOCX files)
def process_resume_resumes():
    resumes = fetch_resume_resumes()
    if not resumes:
        print("No resumes found in the resume folder.")
        return []

    data = []
    for resume in resumes:
        try:
            print(f"Processing: {resume['name']}")
            resume_text = extract_text(resume["path"])
            if not resume_text.strip():
                print(f"Skipping {resume['name']} due to empty text extraction.")
                continue
                
            # Extract only essential information to reduce API load
            essential_resume_text = extract_essential_resume_info(resume_text)
            
            scores = score_resume(JOB_DESCRIPTION, essential_resume_text)
            if "total_score" not in scores:
                print(f"Skipping {resume['name']} due to missing score data.")
                continue

            # Use file path as link for local files
            data.append([resume["name"], f"file://{resume['path']}"] + [scores.get(key, 0) for key in CRITERIA_DEFINITIONS.keys()])
        except Exception as e:
            print(f"Error processing {resume['name']}: {e}")

    return data


# Ensure the 'data' directory exists before saving the CSV file
def ensure_directory_exists(file_path):
    csv_directory = os.path.dirname(file_path)
    if csv_directory and not os.path.exists(csv_directory):
        os.makedirs(csv_directory)


# Save results to CSV with Definitions
def save_results_to_csv(data, csv_file_path):
    if not data:
        print("No data available to save.")
        return

    ensure_directory_exists(csv_file_path)

    # Column headers using criteria from config
    columns = ["Candidate Name", "Resume Link"] + list(CRITERIA_DEFINITIONS.keys())

    df = pd.DataFrame(data, columns=pd.Index(columns))

    # Add criteria definitions as the first row
    definition_row = pd.DataFrame([["", ""] + list(CRITERIA_DEFINITIONS.values())], columns=pd.Index(columns))

    # Combine definition row and scores
    df_final = pd.concat([definition_row, df], ignore_index=True)

    # Save to CSV
    df_final.to_csv(csv_file_path, index=False)
    print(f"Results saved in {csv_file_path}")


if __name__ == "__main__":
    # Process DOCX resumes from resume/Resumes folder
    resume_results = process_resume_resumes()
    save_results_to_csv(resume_results, RESUME_CSV_FILE_PATH)