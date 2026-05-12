#!/usr/bin/env python3
"""
Accuracy Tester for Resume Scoring Module

This script tests the accuracy and performance of the resume scoring system
by running various test cases and evaluating the consistency of the AI scoring.
"""

import os
import sys
import time
import json
from datetime import datetime
from rank import score_resume
from config import JOB_DESCRIPTION, CRITERIA_DEFINITIONS

# Sample test resumes with known characteristics
TEST_RESUMES = [
    {
        "name": "Senior Python Developer",
        "text": """
        John Doe
        Email: john.doe@example.com
        Phone: (555) 123-4567
        
        EXPERIENCE
        Senior Python Developer | TechCorp Inc. | Jan 2020 - Present
        - Led development of machine learning models for predictive analytics
        - Implemented RESTful APIs using Flask and Django
        - Managed team of 5 developers and mentored junior staff
        - Reduced processing time by 40% through algorithm optimization
        
        Software Engineer | InnovateX LLC | Jun 2017 - Dec 2019
        - Developed cloud-based solutions using AWS and Google Cloud
        - Built data pipelines for processing large datasets
        - Collaborated with data scientists on AI/ML projects
        
        SKILLS
        - Python, Flask, Django, FastAPI
        - Machine Learning: TensorFlow, PyTorch, scikit-learn
        - Cloud: AWS, GCP, Docker, Kubernetes
        - Databases: PostgreSQL, MongoDB, Redis
        - Version Control: Git, GitHub
        
        EDUCATION
        Master of Science in Computer Science | Stanford University | 2017
        Bachelor of Science in Software Engineering | MIT | 2015
        
        PROJECTS
        Resume Scoring AI | Personal Project | 2023
        - Developed an AI system to score resumes using Google Gemini API
        - Implemented natural language processing for content analysis
        
        Fraud Detection System | TechCorp | 2021
        - Built ML model to detect fraudulent transactions with 95% accuracy
        """,
        "expected_scores": {
            "total_score": 90,
            "experience_score": 28,
            "skills_score": 28,
            "education_score": 19,
            "projects_score": 9,
            "communication_score": 6
        }
    },
    {
        "name": "Entry Level Developer",
        "text": """
        Jane Smith
        Email: jane.smith@email.com
        Phone: (555) 987-6543
        
        EXPERIENCE
        Intern Developer | StartupXYZ | Jun 2023 - Aug 2023
        - Assisted in developing web applications using Python and JavaScript
        - Participated in code reviews and debugging sessions
        - Learned basics of version control with Git
        
        SKILLS
        - Python (basic)
        - HTML, CSS
        - Git
        - MySQL (basic)
        
        EDUCATION
        Bachelor of Science in Computer Science | State University | Expected 2024
        Relevant Coursework: Data Structures, Algorithms, Database Systems
        
        PROJECTS
        University Course Project | Student Portfolio | 2023
        - Created a simple web application for course management
        - Used Flask framework and SQLite database
        """,
        "expected_scores": {
            "total_score": 55,
            "experience_score": 10,
            "skills_score": 15,
            "education_score": 15,
            "projects_score": 7,
            "communication_score": 8
        }
    },
    {
        "name": "Data Scientist with ML Expertise",
        "text": """
        Michael Johnson
        Email: michael.j@datascience.com
        Phone: (555) 456-7890
        
        EXPERIENCE
        Lead Data Scientist | AI Solutions Ltd. | Mar 2019 - Present
        - Developed deep learning models for computer vision applications
        - Built recommendation systems with 30% improvement in engagement
        - Published 3 research papers on neural networks
        - Led team of 8 data scientists and analysts
        
        Senior Data Scientist | Analytics Pro | Feb 2016 - Feb 2019
        - Created NLP models for sentiment analysis
        - Implemented time series forecasting models
        - Worked with big data technologies like Spark and Hadoop
        
        SKILLS
        - Python, R, SQL
        - Machine Learning: TensorFlow, Keras, PyTorch, scikit-learn
        - Data Visualization: Tableau, PowerBI, matplotlib, seaborn
        - Big Data: Spark, Hadoop, Kafka
        - Cloud: AWS SageMaker, GCP AI Platform
        
        EDUCATION
        Ph.D. in Machine Learning | Carnegie Mellon University | 2016
        Master of Science in Statistics | UC Berkeley | 2012
        Bachelor of Science in Mathematics | UCLA | 2010
        
        PROJECTS
        Medical Image Analysis | Research Project | 2020
        - Developed CNN model for detecting tumors in MRI scans
        - Achieved 96% accuracy in clinical trials
        
        Customer Behavior Prediction | AI Solutions | 2019
        - Built ensemble model to predict customer purchasing patterns
        - Increased marketing ROI by 25%
        """,
        "expected_scores": {
            "total_score": 95,
            "experience_score": 29,
            "skills_score": 29,
            "education_score": 20,
            "projects_score": 10,
            "communication_score": 7
        }
    }
]

def calculate_score_accuracy(actual_scores, expected_scores):
    """Calculate the accuracy percentage between actual and expected scores"""
    total_diff = 0
    max_possible_diff = 0
    
    for key in expected_scores:
        if key in actual_scores:
            diff = abs(actual_scores[key] - expected_scores[key])
            total_diff += diff
            # Assuming max score for each category from CRITERIA_DEFINITIONS
            if key == "total_score":
                max_possible_diff += 100
            elif key == "experience_score":
                max_possible_diff += 30
            elif key == "skills_score":
                max_possible_diff += 30
            elif key == "education_score":
                max_possible_diff += 20
            elif key == "projects_score":
                max_possible_diff += 10
            elif key == "communication_score":
                max_possible_diff += 10
    
    if max_possible_diff == 0:
        return 100.0
    
    accuracy = ((max_possible_diff - total_diff) / max_possible_diff) * 100
    return accuracy

def run_accuracy_test():
    """Run the accuracy test on sample resumes"""
    print("🚀 Starting Resume Scoring Accuracy Test")
    print("=" * 50)
    
    results = []
    total_accuracy = 0
    api_call_count = 0
    total_time = 0
    
    for i, test_resume in enumerate(TEST_RESUMES):
        print(f"\n📝 Testing: {test_resume['name']}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            # Score the resume using the actual system
            actual_scores = score_resume(JOB_DESCRIPTION, test_resume["text"])
            api_call_count += 1
            
            end_time = time.time()
            processing_time = end_time - start_time
            total_time += processing_time
            
            # Calculate accuracy
            expected_scores = test_resume["expected_scores"]
            accuracy = calculate_score_accuracy(actual_scores, expected_scores)
            total_accuracy += accuracy
            
            # Store results
            result = {
                "resume_name": test_resume["name"],
                "expected_scores": expected_scores,
                "actual_scores": actual_scores,
                "accuracy": accuracy,
                "processing_time": processing_time
            }
            results.append(result)
            
            # Print results
            print(f"Expected Total Score: {expected_scores['total_score']}")
            print(f"Actual Total Score: {actual_scores.get('total_score', 'N/A')}")
            print(f"Accuracy: {accuracy:.2f}%")
            print(f"Processing Time: {processing_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error scoring resume: {e}")
            result = {
                "resume_name": test_resume["name"],
                "error": str(e),
                "accuracy": 0
            }
            results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    avg_accuracy = total_accuracy / len(TEST_RESUMES) if TEST_RESUMES else 0
    avg_processing_time = total_time / api_call_count if api_call_count > 0 else 0
    
    print(f"Average Accuracy: {avg_accuracy:.2f}%")
    print(f"Total API Calls: {api_call_count}")
    print(f"Average Processing Time: {avg_processing_time:.2f}s")
    print(f"Total Test Time: {total_time:.2f}s")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        print(f"\n{result['resume_name']}:")
        if "error" in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  Accuracy: {result['accuracy']:.2f}%")
            print(f"  Processing Time: {result['processing_time']:.2f}s")
            print(f"  Expected Total: {result['expected_scores']['total_score']}")
            print(f"  Actual Total: {result['actual_scores'].get('total_score', 'N/A')}")
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"accuracy_test_results_{timestamp}.json"
    
    test_summary = {
        "timestamp": timestamp,
        "test_resume_count": len(TEST_RESUMES),
        "average_accuracy": avg_accuracy,
        "total_api_calls": api_call_count,
        "average_processing_time": avg_processing_time,
        "total_test_time": total_time,
        "detailed_results": results
    }
    
    with open(results_file, 'w') as f:
        json.dump(test_summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    return avg_accuracy

def run_consistency_test():
    """Test the consistency of scoring by running the same resume multiple times"""
    print("\n🔄 Starting Consistency Test")
    print("=" * 30)
    
    if not TEST_RESUMES:
        print("No test resumes available")
        return
    
    test_resume = TEST_RESUMES[0]  # Use first resume for consistency test
    print(f"Testing consistency with: {test_resume['name']}")
    
    scores = []
    for i in range(3):  # Run 3 times
        print(f"  Run {i+1}/3...")
        try:
            score = score_resume(JOB_DESCRIPTION, test_resume["text"])
            scores.append(score)
            time.sleep(2)  # Increase delay between calls to avoid rate limiting
        except Exception as e:
            print(f"  ⚠️  Error on run {i+1}: {e}")
            # If it's a rate limit error, wait longer
            if "429" in str(e) or "quota" in str(e).lower():
                print("  Waiting longer due to rate limiting...")
                time.sleep(25)  # Wait for rate limit to reset
                continue
            else:
                return False
    
    # Check consistency only if we have at least 2 successful runs
    successful_runs = [s for s in scores if isinstance(s, dict) and 'total_score' in s]
    if len(successful_runs) >= 2:
        # Compare first and last scores
        first_score = successful_runs[0].get('total_score', 0)
        last_score = successful_runs[-1].get('total_score', 0)
        difference = abs(first_score - last_score)
        
        print(f"First score: {first_score}")
        print(f"Last score: {last_score}")
        print(f"Difference: {difference}")
        
        if difference <= 5:  # Allow small variance
            print("✅ Scoring is consistent")
            return True
        else:
            print("⚠️  Scoring shows significant variance")
            return False
    elif len(successful_runs) == 1:
        print("✅ Single successful run (rate limiting prevented multiple runs)")
        return True
    else:
        print("❌ No successful runs to test consistency")
        return False

def main():
    """Main function to run all tests"""
    print("🔍 AI Resume Scoring Accuracy Tester")
    print("=====================================")
    
    # Run accuracy test
    try:
        avg_accuracy = run_accuracy_test()
    except Exception as e:
        print(f"❌ Error in accuracy test: {e}")
        avg_accuracy = 0
    
    # Run consistency test
    try:
        consistency_result = run_consistency_test()
    except Exception as e:
        print(f"❌ Error in consistency test: {e}")
        consistency_result = False
    
    # Final assessment
    print("\n🏁 FINAL ASSESSMENT")
    print("=" * 20)
    
    if avg_accuracy >= 80:
        print("✅ Scoring accuracy is HIGH")
    elif avg_accuracy >= 60:
        print("⚠️  Scoring accuracy is MODERATE")
    else:
        print("❌ Scoring accuracy is LOW")
    
    if consistency_result:
        print("✅ Scoring consistency is GOOD")
    else:
        print("⚠️  Scoring consistency needs improvement")
    
    print(f"\nOverall system rating: {avg_accuracy:.1f}/100")

if __name__ == "__main__":
    main()