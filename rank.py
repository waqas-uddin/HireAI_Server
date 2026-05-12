import requests
import json
import config

# Use a more stable and widely available model
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={config.GOOGLE_API_KEY}"

def score_resume(job_description, resume_text):
    # Generate criteria breakdown from config
    criteria_prompt = "\n".join([f"- {desc}" for desc in config.CRITERIA_DEFINITIONS.values()])

    prompt = f"""
    You are an expert recruiter. Given a job description and a candidate's resume, 
    score the resume based ONLY on the following criteria. Focus ONLY on the essential 
    information provided in the resume that relates to these criteria:

    {criteria_prompt}

    **Job Description:**
    {job_description}

    **Candidate Resume (Essential Information Only):**
    {resume_text}

    Provide ONLY a valid JSON object without explanations, in the exact format:

    {{
        {", ".join([f'"{key}": <int>' for key in config.CRITERIA_DEFINITIONS.keys()])},
        "reasoning": "A concise breakdown of why these scores were given, referencing specific items in the resume."
    }}

    IMPORTANT: 
    - Analyze only the provided essential resume information
    - Do not make assumptions about missing information
    - Assign scores based solely on explicit information in the resume
    - Respond with JSON only, with no additional text or explanations.
    """

    # Default scores in case of API failure
    default_scores = {
        "total_score": 75,
        "experience_score": 25,
        "skills_score": 20,
        "education_score": 15,
        "projects_score": 10,
        "communication_score": 5,
        "reasoning": "Fallback scores applied due to AI connection issues."
    }
    
    # If the API key is not set or is the placeholder, return default scores
    if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "YOUR_REAL_GEMINI_API_KEY_HERE":
        print("Using default scores (no valid API key configured)")
        return default_scores

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(API_URL, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            response_json = response.json()
            
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                ai_output = response_json["candidates"][0]["content"]["parts"][0]["text"]
                
                # Clean the JSON response
                cleaned_json = ai_output.strip()
                # Remove markdown code block markers if present
                cleaned_json = cleaned_json.replace("```json", "").replace("```", "").strip()
                
                # Try to parse the JSON
                try:
                    scores = json.loads(cleaned_json)
                    print(f"API Response: {scores}")
                    return scores
                except json.JSONDecodeError as je:
                    print(f"Failed to parse API response as JSON: {je}")
                    print(f"Raw API response: {cleaned_json}")
                    return default_scores
            else:
                print("API returned unexpected response structure")
                print(f"Response: {response_json}")
                return default_scores
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return default_scores
            
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return default_scores