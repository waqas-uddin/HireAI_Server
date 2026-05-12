import requests
import json
import config

# API URLs
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={config.GOOGLE_API_KEY}"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(prompt):
    """Utility to call Groq API with the given prompt"""
    if not hasattr(config, 'GROQ_API_KEY') or not config.GROQ_API_KEY or "gsk_" not in config.GROQ_API_KEY:
        raise ValueError("Groq API key not configured")

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a professional technical recruiter. You MUST respond with a valid JSON object only. Do not include markdown code blocks or conversational text."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

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
    
    # 1. Try Groq first (as requested)
    try:
        print("Attempting to score resume using Groq...")
        groq_response = call_groq(prompt)
        scores = json.loads(groq_response)
        print(f"Groq Success: {scores}")
        return scores
    except Exception as e:
        print(f"Groq failed, falling back to Gemini: {str(e)}")

    # 2. Fallback to Gemini
    if not config.GOOGLE_API_KEY or "AIza" not in config.GOOGLE_API_KEY:
        print("Gemini API key not configured, returning default scores.")
        return default_scores

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        print("Attempting to score resume using Gemini...")
        response = requests.post(GEMINI_API_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        
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
                    print(f"Gemini Success: {scores}")
                    return scores
                except json.JSONDecodeError as je:
                    print(f"Failed to parse Gemini response as JSON: {je}")
                    return default_scores
            else:
                print("Gemini returned unexpected response structure")
                return default_scores
        else:
            print(f"Gemini API Error: {response.status_code}")
            return default_scores
            
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return default_scores