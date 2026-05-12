import requests
import json
from config import GOOGLE_API_KEY

def verify_api_key():
    """Verify if the API key is valid by making a simple request to the Gemini API"""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY in ["YOUR_REAL_GEMINI_API_KEY_HERE"]:
        print("❌ No valid API key found in config.py")
        print("Please update GOOGLE_API_KEY with your actual Gemini API key")
        # Let user input the key directly for testing
        user_key = input("Enter your actual Gemini API key for testing (or press Enter to skip): ").strip()
        if user_key:
            return test_key(user_key)
        return False
    
    return test_key(GOOGLE_API_KEY)

def test_key(api_key):
    """Test a specific API key"""
    print(f"Testing API key: {api_key[:10]}..." if len(api_key) > 10 else "Testing API key...")
    
    # Test API key with a simple request
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    test_payload = {
        "contents": [{
            "parts": [{
                "text": "Respond with exactly: API_KEY_VALID"
            }]
        }]
    }
    
    try:
        response = requests.post(
            test_url,
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result:
                reply = result["candidates"][0]["content"]["parts"][0]["text"]
                if "API_KEY_VALID" in reply:
                    print(f"✅ API key is valid!")
                    return True
                else:
                    print(f"✅ API key works but unexpected response: {reply}")
                    return True
            else:
                print(f"❌ API returned unexpected response: {result}")
                return False
        elif response.status_code == 400:
            error_result = response.json()
            if "error" in error_result and "API key not valid" in error_result["error"].get("message", ""):
                print(f"❌ API key is invalid: {error_result['error']['message']}")
                return False
            else:
                print(f"❌ API Error (400): {response.text}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API key: {e}")
        return False

if __name__ == "__main__":
    print("Verifying Gemini API key...")
    print("=" * 40)
    if verify_api_key():
        print("\n✅ Your API key is working! The resume scoring will now provide actual results.")
    else:
        print("\n❌ API key verification failed. Please check your key and try again.")