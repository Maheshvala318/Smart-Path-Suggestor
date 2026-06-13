import requests
import json
import os

def test_groq_fallback(text):
    url = "http://localhost:5050/api/parse-intent"
    payload = {"text": text}
    
    # We will temporarily mock the absence of GEMINI_API_KEY in the request 
    # Or just rely on the fact that if it fails, it falls back.
    # To TRULY test fallback, we can send a request and check the 'method' in response.
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        print(f"Transcript: '{text}'")
        print(f"Response Method: {data.get('method')}")
        print(f"Source: {data.get('source')}")
        print(f"Destination: {data.get('destination')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Groq LLM Fallback (will use Groq if Gemini fails/quota exceeded)...")
    test_groq_fallback("navigate from the main door to the seminar hall")
    test_groq_fallback("take me to lab 4 from office")
