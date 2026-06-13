import requests
import json

def test_integrated_parse(text):
    url = "http://localhost:5050/api/parse-intent"
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if response.status_code == 200:
            print(f"Transcript: '{text}'")
            print(f"  Extracted Source: {data.get('source')}")
            print(f"  Extracted Destination: {data.get('destination')}")
        else:
            print(f"Failed to parse '{text}': {data.get('error')}")
    except Exception as e:
        print(f"Error connecting to main server: {e}")

if __name__ == "__main__":
    print("Testing Integrated Voice Intent Extraction...")
    print("-" * 40)
    test_integrated_parse("I want to go from the main door to the seminar hall")
    test_integrated_parse("navigate to washroom from the office")
