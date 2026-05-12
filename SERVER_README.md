# AI Resume Ranker Server

This document explains how to run the AI Resume Ranker application as a web server.

## Prerequisites

1. Python 3.7 or higher
2. Required Python packages (installed via `pip install -r requirements.txt`)
3. Flask (installed via `pip install flask`)
4. python-docx (installed via `pip install python-docx`)

## Running the Server

1. Navigate to the project directory:
   ```
   cd AI-ResumeRank
   ```

2. Run the server:
   ```
   python server.py
   ```

3. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Features

- Web interface for triggering resume processing
- Real-time status updates during processing
- Display of results in a table format
- CSV export of results
- Resume upload functionality
- Individual resume scoring capability

## Configuration

To use the Gemini API:

1. Generate a Google Gemini API key
2. Update `config.py` with your actual Google API key
3. Ensure your resume folders are properly configured:
   - `data/CVs` for PDF resumes
   - `data/resume/Resumes` for DOCX resumes

## How It Works

The server provides a web interface that allows you to:
1. Upload new resumes (PDF format)
2. Process all resumes in the configured folders
3. View real-time processing status
4. See results in a tabular format
5. Score individual resumes on demand

## File Structure

The application organizes resumes in the following structure:
- `data/CVs/` - PDF resumes processed for the main CSV
- `data/resume/Resumes/` - DOCX resumes processed for the separate CSV
- `data/uploads/` - Resumes uploaded through the web interface
- `data/resumes.csv` - Results for PDF resumes
- `data/resume_Resumes_resumes.csv` - Results for DOCX resumes