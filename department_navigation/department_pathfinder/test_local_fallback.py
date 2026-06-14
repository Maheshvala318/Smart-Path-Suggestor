import requests
import json

def test_local_fallback(text):
    url = "http://localhost:5050/api/parse-intent"
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if response.status_code == 200:
            print(f"Transcript: '{text}'")
            print(f"  Data: {json.dumps(data, indent=2)}")
        else:
            print(f"Failed: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Local Fallback & Cache...")
    print("-" * 40)
    # This should be handled by regex
    test_local_fallback("from 1 to 5")
    # This should be handled by cache (same text)
    test_local_fallback("from 1 to 5")
    # This should be handled by regex
    test_local_fallback("navigate to 21 from 4")
