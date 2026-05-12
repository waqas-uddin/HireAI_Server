#!/usr/bin/env python3
"""
Test Runner for Resume Scoring Module

This script provides a convenient way to run all tests for the resume scoring system.
"""

import subprocess
import sys
import os

def run_test_script(script_name, description):
    """Run a test script and return the result"""
    print(f"\n{'='*50}")
    print(f"Running {description}")
    print(f"{'='*50}")
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), script_name)
        ], capture_output=True, text=True, timeout=120)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main function to run all tests"""
    print("🔍 Resume Scoring System Test Runner")
    print("===================================")
    
    # Check if API key is configured
    try:
        from config import GOOGLE_API_KEY
        if not GOOGLE_API_KEY or GOOGLE_API_KEY in ["YOUR_REAL_GEMINI_API_KEY_HERE", ""]:
            print("⚠️  Warning: API key not configured in config.py")
            print("   Some tests may use default scores instead of actual AI scoring")
    except ImportError:
        print("❌ Could not import config.py")
        return
    
    # Run tests
    tests = [
        ("verify_api.py", "API Key Verification"),
        ("quick_test.py", "Quick Resume Scoring Test"),
        ("test_accuracy.py", "Full Accuracy Test"),
        ("visualize_accuracy.py", "Accuracy Visualization")
    ]
    
    results = []
    for script_name, description in tests:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        if os.path.exists(script_path):
            success = run_test_script(script_name, description)
            results.append((description, success))
        else:
            print(f"\n⚠️  Skipping {description} (script not found)")
            results.append((description, False))
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{description}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()