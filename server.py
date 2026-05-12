import os
import sys
from flask import Flask, render_template, jsonify, request, redirect, url_for
import threading
import time
import uuid
from werkzeug.utils import secure_filename
from main import process_resume_resumes, save_results_to_csv
from rank import score_resume
import PyPDF2
from docx import Document
from config import UPLOADED_RESUME_FOLDER, JOB_DESCRIPTION, RESUME_CSV_FILE_PATH
from drive import fetch_resume_resumes
import subprocess
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOADED_RESUME_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variable to store processing status
processing_status = {
    "is_processing": False,
    "message": "",
    "results": None
}

# Global variable to store individual scoring result
individual_score_result = {
    "is_scoring": False,
    "result": None,
    "error": None
}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Resume Ranker</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .btn { background-color: #4CAF50; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border: none; border-radius: 5px; }
            .btn:hover { background-color: #45a049; }
            .btn-upload { background-color: #2196F3; }
            .btn-upload:hover { background-color: #0b7dda; }
            .btn-reset { background-color: #f44336; }
            .btn-reset:hover { background-color: #d32f2f; }
            .btn-score { background-color: #FF9800; }
            .btn-score:hover { background-color: #e68a00; }
            .status { margin-top: 20px; padding: 15px; border-radius: 5px; }
            .processing { background-color: #fff3cd; border: 1px solid #ffeaa7; }
            .success { background-color: #d4edda; border: 1px solid #c3e6cb; }
            .error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
            .results { margin-top: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .file-link { color: #1a73e8; text-decoration: none; }
            .file-link:hover { text-decoration: underline; }
            .upload-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            input[type=file] { margin: 10px 0; }
            .action-buttons { display: flex; gap: 10px; margin: 20px 0; flex-wrap: wrap; }
            .score-result { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
            .score-item { margin: 10px 0; }
            .score-value { font-weight: bold; color: #2196F3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Resume Ranker</h1>
            <p>This application processes resumes from your local folder and ranks them using AI.</p>
            
            <div class="upload-section">
                <h2>Upload New Resume</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input type="file" id="resumeFile" name="resume" accept=".pdf" required>
                    <button type="submit" class="btn btn-upload">Upload Resume</button>
                </form>
                <div id="uploadStatus"></div>
            </div>
            
            <div class="upload-section">
                <h2>Score Individual Resume</h2>
                <p>Select an uploaded resume to score it individually:</p>
                <select id="resumeSelect">
                    <option value="">Select a resume...</option>
                </select>
                <button class="btn btn-score" onclick="scoreIndividualResume()">Score Resume</button>
                <div id="individualScoreStatus"></div>
                <div id="individualScoreResult"></div>
            </div>
            
            <div class="action-buttons">
                <button class="btn" onclick="startProcessing()">Process All Resumes</button>
                <button class="btn btn-reset" onclick="resetResults()">Reset Results</button>
                <button class="btn" onclick="loadUploadedResumes()">Refresh Resume List</button>
            </div>
            
            <div id="status"></div>
            <div id="results"></div>
        </div>

        <script>
            // Load uploaded resumes on page load
            window.onload = function() {
                loadUploadedResumes();
            };
            
            // Handle file upload
            document.getElementById('uploadForm').addEventListener('submit', function(e) {
                e.preventDefault();
                const fileInput = document.getElementById('resumeFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    updateUploadStatus('Please select a file to upload.', 'error');
                    return;
                }
                
                const formData = new FormData();
                formData.append('resume', file);
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    updateUploadStatus(data.message, data.success ? 'success' : 'error');
                    if (data.success) {
                        fileInput.value = ''; // Clear the file input
                        loadUploadedResumes(); // Refresh the resume list
                    }
                })
                .catch(error => {
                    updateUploadStatus('Error uploading file: ' + error, 'error');
                });
            });
            
            function updateUploadStatus(message, type) {
                const statusDiv = document.getElementById('uploadStatus');
                statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function loadUploadedResumes() {
                fetch('/uploaded_resumes')
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById('resumeSelect');
                    select.innerHTML = '<option value="">Select a resume...</option>';
                    data.resumes.forEach(resume => {
                        const option = document.createElement('option');
                        option.value = resume;
                        option.textContent = resume;
                        select.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('Error loading resumes:', error);
                });
            }

            function startProcessing() {
                fetch('/process', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        updateStatus(data.message, 'processing');
                        checkStatus();
                    })
                    .catch(error => {
                        updateStatus('Error starting processing: ' + error, 'error');
                    });
            }
            
            function resetResults() {
                fetch('/reset', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('results').innerHTML = '';
                        updateStatus(data.message, 'success');
                    })
                    .catch(error => {
                        updateStatus('Error resetting results: ' + error, 'error');
                    });
            }
            
            function scoreIndividualResume() {
                const select = document.getElementById('resumeSelect');
                const filename = select.value;
                
                if (!filename) {
                    updateIndividualScoreStatus('Please select a resume to score.', 'error');
                    return;
                }
                
                updateIndividualScoreStatus('Scoring resume...', 'processing');
                document.getElementById('individualScoreResult').innerHTML = '';
                
                fetch('/score_resume', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({filename: filename})
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Score response:', data);  // Debug log
                    if (data.error) {
                        updateIndividualScoreStatus(data.error, 'error');
                    } else {
                        updateIndividualScoreStatus('Scoring completed!', 'success');
                        displayIndividualScoreResult(data);
                    }
                })
                .catch(error => {
                    console.error('Scoring error:', error);  // Debug log
                    updateIndividualScoreStatus('Error scoring resume: ' + error, 'error');
                });
            }
            
            function updateIndividualScoreStatus(message, type) {
                const statusDiv = document.getElementById('individualScoreStatus');
                statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            }
            
            function displayIndividualScoreResult(scores) {
                const resultDiv = document.getElementById('individualScoreResult');
                let html = '<div class="score-result"><h3>AI-Verified Scoring Breakdown</h3>';
                
                if (scores && typeof scores === 'object') {
                    html += `<div class="score-item"><strong>Total Score:</strong> <span class="score-value">${scores.total_score || 0}/100</span></div>`;
                    html += `<div class="score-item">Experience: <span class="score-value">${scores.experience_score || 0}/30</span></div>`;
                    html += `<div class="score-item">Skills Match: <span class="score-value">${scores.skills_score || 0}/30</span></div>`;
                    html += `<div class="score-item">Education: <span class="score-value">${scores.education_score || 0}/20</span></div>`;
                    html += `<div class="score-item">Projects: <span class="score-value">${scores.projects_score || 0}/10</span></div>`;
                    html += `<div class="score-item">Communication: <span class="score-value">${scores.communication_score || 0}/10</span></div>`;
                    
                    if (scores.reasoning) {
                        html += `<div class="score-item" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
                                    <strong>AI Reasoning:</strong>
                                    <p style="font-size: 0.9rem; color: #666; line-height: 1.5;">${scores.reasoning}</p>
                                 </div>`;
                    }
                } else {
                    html += '<div class="score-item">Error: Invalid score data received</div>';
                }
                
                html += '</div>';
                resultDiv.innerHTML = html;
            }

            function checkStatus() {
                fetch('/status')
                    .then(response => response.json())
                    .then(data => {
                        updateStatus(data.message, data.is_processing ? 'processing' : (data.results ? 'success' : 'error'));
                        if (data.is_processing) {
                            setTimeout(checkStatus, 2000);
                        } else if (data.results) {
                            displayResults(data.results);
                        }
                    })
                    .catch(error => {
                        updateStatus('Error checking status: ' + error, 'error');
                    });
            }

            function updateStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = `<div class="status ${type}">${message}</div>`;
            }

            function displayResults(results) {
                const resultsDiv = document.getElementById('results');
                if (results && results.length > 0) {
                    let tableHtml = '<div class="results"><h2>Results</h2><table><tr>';
                    // Header row
                    results[0].forEach((header, index) => {
                        tableHtml += `<th>${header}</th>`;
                    });
                    tableHtml += '</tr>';
                    
                    // Data rows (skip first row which contains definitions)
                    for (let i = 1; i < results.length; i++) {
                        tableHtml += '<tr>';
                        results[i].forEach((cell, index) => {
                            if (index === 1 && cell.startsWith('file://')) {
                                // Make the file link clickable
                                const filePath = cell.substring(7); // Remove 'file://' prefix
                                tableHtml += `<td><a href="${cell}" class="file-link" target="_blank">Open File</a></td>`;
                            } else {
                                tableHtml += `<td>${cell}</td>`;
                            }
                        });
                        tableHtml += '</tr>';
                    }
                    tableHtml += '</table></div>';
                    resultsDiv.innerHTML = tableHtml;
                }
            }
        </script>
    </body>
    </html>
    '''

# Extract text from a PDF file
def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"success": False, "message": "No file provided"})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"})
    
    if file and file.filename and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"success": True, "message": f"File {filename} uploaded successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid file type. Please upload a PDF file."})

@app.route('/uploaded_resumes')
def get_uploaded_resumes():
    try:
        resumes = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.endswith('.pdf'):
                    resumes.append(filename)
        return jsonify({"resumes": resumes})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/score_resume', methods=['POST'])
def score_individual_resume():
    global individual_score_result
    
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"error": "No filename provided"})
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"})
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file_path)
        
        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from resume"})
        
        # Extract only essential information to reduce API load
        from main import extract_essential_resume_info
        essential_resume_text = extract_essential_resume_info(resume_text)
        
        # Score the resume
        scores = score_resume(JOB_DESCRIPTION, essential_resume_text)
        
        print(f"Returning scores: {scores}")  # Debug log
        return jsonify(scores)
    except Exception as e:
        print(f"Error in score_individual_resume: {str(e)}")  # Debug log
        return jsonify({"error": f"Error scoring resume: {str(e)}"})

@app.route('/process', methods=['POST'])
def start_processing():
    global processing_status
    
    if processing_status["is_processing"]:
        return jsonify({"message": "Already processing resumes..."})
    
    processing_status["is_processing"] = True
    processing_status["message"] = "Starting resume processing..."
    processing_status["results"] = None
    
    # Start processing in a separate thread
    thread = threading.Thread(target=process_resumes_thread)
    thread.start()
    
    return jsonify({"message": "Started processing resumes..."})

def process_resumes_thread():
    global processing_status
    try:
        processing_status["message"] = "Fetching resumes from local folder..."
        results = process_all_resumes()
        
        processing_status["results"] = results
        processing_status["message"] = "Processing completed successfully!"
    except Exception as e:
        processing_status["message"] = f"Error processing resumes: {str(e)}"
        print(f"Error: {str(e)}", file=sys.stderr)
    finally:
        processing_status["is_processing"] = False

@app.route('/status')
def get_status():
    global processing_status
    return jsonify(processing_status)

@app.route('/reset', methods=['POST'])
def reset_results():
    global processing_status
    processing_status = {
        "is_processing": False,
        "message": "Results reset successfully",
        "results": None
    }
    # Clear the CSV file
    if os.path.exists(RESUME_CSV_FILE_PATH):
        os.remove(RESUME_CSV_FILE_PATH)
    return jsonify({"message": "Results reset successfully"})

def process_all_resumes():
    """Process all resumes in the resume folder"""
    try:
        # Process DOCX resumes from resume/Resumes folder
        resume_results = process_resume_resumes()
        save_results_to_csv(resume_results, RESUME_CSV_FILE_PATH)
        
        # Read the CSV file to return results
        import pandas as pd
        if os.path.exists(RESUME_CSV_FILE_PATH):
            df = pd.read_csv(RESUME_CSV_FILE_PATH)
            return [df.columns.tolist()] + df.values.tolist()
        else:
            return []
    except Exception as e:
        print(f"Error processing resumes: {str(e)}", file=sys.stderr)
        raise e

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        data = request.get_json()
        language = data.get('language')
        code = data.get('code')
        
        if not language or not code:
            return jsonify({"error": "Language and code are required"}), 400

        # Create a temporary file to run the code
        suffix = '.py' if language == 'python' else '.js'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(code.encode('utf-8'))
            temp_file_path = f.name

        try:
            if language == 'python':
                # Use current python executable
                cmd = [sys.executable, temp_file_path]
            else: # javascript/node
                # Assume 'node' is in PATH
                cmd = ['node', temp_file_path]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            output = result.stdout + result.stderr
            return jsonify({"run": {"output": output or "Program executed with no output."}})
        except subprocess.TimeoutExpired:
            return jsonify({"run": {"output": "Error: Execution timed out (10s limit)."}})
        except Exception as e:
            return jsonify({"run": {"output": f"Error: {str(e)}. Make sure {language} is installed on the host machine."}})
        finally:
            if os.path.exists(temp_file_path):
                try: os.remove(temp_file_path)
                except: pass

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)