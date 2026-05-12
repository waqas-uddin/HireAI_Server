#!/usr/bin/env python3
"""
Visualization Script for Resume Scoring Accuracy

This script generates heatmaps and charts to visualize the accuracy of the resume scoring model.
"""

import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure matplotlib to use a non-interactive backend
plt.switch_backend('Agg')

def load_latest_test_results():
    """Load the most recent test results file"""
    # Find the most recent accuracy test results file
    test_files = [f for f in os.listdir('.') if f.startswith('accuracy_test_results_') and f.endswith('.json')]
    
    if not test_files:
        print("No test results files found. Run the accuracy test first.")
        return None
    
    # Sort by timestamp to get the most recent
    test_files.sort(reverse=True)
    latest_file = test_files[0]
    
    try:
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading test results: {e}")
        return None

def create_accuracy_heatmap(test_data):
    """Create a heatmap showing the accuracy of different scoring categories"""
    if not test_data or 'detailed_results' not in test_data:
        print("Invalid test data format")
        return
    
    results = test_data['detailed_results']
    
    # Prepare data for heatmap
    resume_names = [result['resume_name'] for result in results if 'error' not in result]
    categories = ['Total Score', 'Experience', 'Skills', 'Education', 'Projects', 'Communication']
    
    # Create matrix for actual scores
    actual_matrix = []
    expected_matrix = []
    
    for result in results:
        if 'error' not in result:
            actual_row = [
                result['actual_scores'].get('total_score', 0),
                result['actual_scores'].get('experience_score', 0),
                result['actual_scores'].get('skills_score', 0),
                result['actual_scores'].get('education_score', 0),
                result['actual_scores'].get('projects_score', 0),
                result['actual_scores'].get('communication_score', 0)
            ]
            expected_row = [
                result['expected_scores'].get('total_score', 0),
                result['expected_scores'].get('experience_score', 0),
                result['expected_scores'].get('skills_score', 0),
                result['expected_scores'].get('education_score', 0),
                result['expected_scores'].get('projects_score', 0),
                result['expected_scores'].get('communication_score', 0)
            ]
            actual_matrix.append(actual_row)
            expected_matrix.append(expected_row)
    
    if not actual_matrix:
        print("No valid results to visualize")
        return
    
    # Convert to numpy arrays
    actual_array = np.array(actual_matrix)
    expected_array = np.array(expected_matrix)
    
    # Create heatmaps
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle('Resume Scoring Accuracy Heatmaps', fontsize=16)
    
    # Heatmap for actual scores
    im1 = axes[0].imshow(actual_array, cmap='Blues', aspect='auto')
    axes[0].set_title('Actual Scores')
    axes[0].set_yticks(range(len(resume_names)))
    axes[0].set_yticklabels(resume_names, rotation=0)
    axes[0].set_xticks(range(len(categories)))
    axes[0].set_xticklabels(categories, rotation=45, ha='right')
    
    # Add text annotations for actual scores
    for i in range(len(resume_names)):
        for j in range(len(categories)):
            axes[0].text(j, i, f'{actual_array[i, j]:.0f}', 
                        ha="center", va="center", color="black" if actual_array[i, j] < 50 else "white")
    
    # Heatmap for expected scores
    im2 = axes[1].imshow(expected_array, cmap='Greens', aspect='auto')
    axes[1].set_title('Expected Scores')
    axes[1].set_yticks(range(len(resume_names)))
    axes[1].set_yticklabels(resume_names, rotation=0)
    axes[1].set_xticks(range(len(categories)))
    axes[1].set_xticklabels(categories, rotation=45, ha='right')
    
    # Add text annotations for expected scores
    for i in range(len(resume_names)):
        for j in range(len(categories)):
            axes[1].text(j, i, f'{expected_array[i, j]:.0f}', 
                        ha="center", va="center", color="black" if expected_array[i, j] < 50 else "white")
    
    # Add colorbars
    plt.colorbar(im1, ax=axes[0], shrink=0.8)
    plt.colorbar(im2, ax=axes[1], shrink=0.8)
    
    plt.tight_layout()
    
    # Save the heatmap
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    heatmap_file = f'accuracy_heatmap_{timestamp}.png'
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved as: {heatmap_file}")
    return heatmap_file

def create_difference_heatmap(test_data):
    """Create a heatmap showing the differences between actual and expected scores"""
    if not test_data or 'detailed_results' not in test_data:
        print("Invalid test data format")
        return
    
    results = test_data['detailed_results']
    
    # Prepare data for difference heatmap
    resume_names = [result['resume_name'] for result in results if 'error' not in result]
    categories = ['Total Score', 'Experience', 'Skills', 'Education', 'Projects', 'Communication']
    
    # Create matrix for differences
    diff_matrix = []
    
    for result in results:
        if 'error' not in result:
            diff_row = [
                abs(result['actual_scores'].get('total_score', 0) - result['expected_scores'].get('total_score', 0)),
                abs(result['actual_scores'].get('experience_score', 0) - result['expected_scores'].get('experience_score', 0)),
                abs(result['actual_scores'].get('skills_score', 0) - result['expected_scores'].get('skills_score', 0)),
                abs(result['actual_scores'].get('education_score', 0) - result['expected_scores'].get('education_score', 0)),
                abs(result['actual_scores'].get('projects_score', 0) - result['expected_scores'].get('projects_score', 0)),
                abs(result['actual_scores'].get('communication_score', 0) - result['expected_scores'].get('communication_score', 0))
            ]
            diff_matrix.append(diff_row)
    
    if not diff_matrix:
        print("No valid results to visualize")
        return
    
    # Convert to numpy array
    diff_array = np.array(diff_matrix)
    
    # Create heatmap for differences
    plt.figure(figsize=(10, 6))
    im = plt.imshow(diff_array, cmap='Reds', aspect='auto')
    plt.title('Absolute Differences Between Actual and Expected Scores')
    
    plt.yticks(range(len(resume_names)), resume_names, rotation=0)
    plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
    
    # Add text annotations for differences
    for i in range(len(resume_names)):
        for j in range(len(categories)):
            plt.text(j, i, f'{diff_array[i, j]:.0f}', 
                    ha="center", va="center", color="white" if diff_array[i, j] > 10 else "black")
    
    plt.colorbar(im, shrink=0.8)
    plt.tight_layout()
    
    # Save the difference heatmap
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    diff_heatmap_file = f'difference_heatmap_{timestamp}.png'
    plt.savefig(diff_heatmap_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Difference heatmap saved as: {diff_heatmap_file}")
    return diff_heatmap_file

def create_accuracy_barchart(test_data):
    """Create a bar chart showing accuracy percentages for each resume"""
    if not test_data or 'detailed_results' not in test_data:
        print("Invalid test data format")
        return
    
    results = [r for r in test_data['detailed_results'] if 'accuracy' in r]
    
    if not results:
        print("No accuracy data to visualize")
        return
    
    resume_names = [result['resume_name'] for result in results]
    accuracies = [result['accuracy'] for result in results]
    
    # Create bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(resume_names)), accuracies, color='skyblue')
    plt.title('Accuracy Percentage for Each Resume')
    plt.xlabel('Resume')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 100)
    
    # Add value labels on bars
    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{acc:.1f}%', ha='center', va='bottom')
    
    plt.xticks(range(len(resume_names)), resume_names, rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the bar chart
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    barchart_file = f'accuracy_barchart_{timestamp}.png'
    plt.savefig(barchart_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Accuracy bar chart saved as: {barchart_file}")
    return barchart_file

def create_summary_report(test_data, heatmap_file, diff_heatmap_file, barchart_file):
    """Create a summary report with all visualizations"""
    if not test_data:
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
Resume Scoring Accuracy Visualization Report
==========================================

Generated on: {timestamp}

Summary Statistics:
- Average Accuracy: {test_data.get('average_accuracy', 0):.2f}%
- Total API Calls: {test_data.get('total_api_calls', 0)}
- Average Processing Time: {test_data.get('average_processing_time', 0):.2f}s

Visualizations Generated:
1. Accuracy Heatmaps: {heatmap_file}
2. Difference Heatmap: {diff_heatmap_file}
3. Accuracy Bar Chart: {barchart_file}

Detailed Results:
"""
    
    for result in test_data.get('detailed_results', []):
        if 'error' in result:
            report += f"\n{result['resume_name']}:\n  ❌ Error: {result['error']}\n"
        else:
            report += f"\n{result['resume_name']}:\n  Accuracy: {result['accuracy']:.2f}%\n"
    
    # Save report
    report_file = f'visualization_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Summary report saved as: {report_file}")

def main():
    """Main function to generate all visualizations"""
    print("🔍 Resume Scoring Accuracy Visualization")
    print("=" * 40)
    
    # Load test results
    test_data = load_latest_test_results()
    if not test_data:
        return
    
    print(f"Loaded test results with {len(test_data.get('detailed_results', []))} resumes")
    
    # Generate visualizations
    heatmap_file = create_accuracy_heatmap(test_data)
    diff_heatmap_file = create_difference_heatmap(test_data)
    barchart_file = create_accuracy_barchart(test_data)
    
    # Create summary report
    create_summary_report(test_data, heatmap_file, diff_heatmap_file, barchart_file)
    
    print("\n✅ All visualizations generated successfully!")

if __name__ == "__main__":
    main()