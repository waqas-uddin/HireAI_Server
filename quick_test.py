#!/usr/bin/env python3
"""
Quick Test Script for Resume Scoring Module

This script provides a simple way to test the resume scoring functionality
with a sample resume and job description.
"""

import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rank import score_resume
from config import JOB_DESCRIPTION

def main():
    # Sample resume text
    sample_resume = """
    Alex Johnson
    Email: alex.johnson@example.com
    Phone: (555) 123-4567
    
    PROFESSIONAL EXPERIENCE
    Senior Python Developer | TechInnovate Inc. | March 2020 - Present
    - Developed AI/ML solutions using Python, TensorFlow, and PyTorch
    - Led a team of 4 developers in creating cloud-based applications
    - Implemented RESTful APIs and microservices architecture
    - Reduced processing time by 35% through code optimization
    
    Software Engineer | DataSystems LLC | June 2017 - February 2020
    - Built data processing pipelines for large-scale analytics
    - Worked with cloud platforms including AWS and Google Cloud
    - Collaborated with data scientists on machine learning projects
    
    SKILLS
    - Programming: Python, JavaScript, SQL
    - AI/ML: TensorFlow, PyTorch, scikit-learn
    - Cloud: AWS, GCP, Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB
    - Tools: Git, Jira, CI/CD
    
    EDUCATION
    Master of Science in Computer Science | Carnegie Mellon University | 2017
    Bachelor of Science in Software Engineering | University of Washington | 2015
    
    PROJECTS
    Intelligent Resume Analyzer | Personal Project | 2023
    - Created an AI system to analyze and score resumes
    - Integrated with Google Gemini API for natural language processing
    
    Predictive Maintenance System | TechInnovate | 2021
    - Developed ML model to predict equipment failures
    - Achieved 92% accuracy in real-world deployment
    """
    
    print("🚀 Quick Resume Scoring Test")
    print("=" * 30)
    print("Job Description:")
    print(JOB_DESCRIPTION[:100] + "..." if len(JOB_DESCRIPTION) > 100 else JOB_DESCRIPTION)
    print("\nScoring sample resume...")
    
    try:
        # Score the resume
        scores = score_resume(JOB_DESCRIPTION, sample_resume)
        
        print("\n📊 Scoring Results:")
        print("-" * 20)
        for key, value in scores.items():
            # Format the key to be more readable
            formatted_key = key.replace('_', ' ').title()
            print(f"{formatted_key}: {value}")
            
        print(f"\n✅ Resume scoring completed successfully!")
        print(f"Total Score: {scores.get('total_score', 'N/A')}/100")
        
    except Exception as e:
        print(f"❌ Error scoring resume: {e}")
        print("Please check your API key and internet connection.")

if __name__ == "__main__":
    main()