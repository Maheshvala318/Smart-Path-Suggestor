import requests
import json

def test_voice_parse(text):
    url = "http://localhost:5001/parse"
    payload = {"text": text}
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if response.status_code == 200:
            print(f"Transcript: '{text}'")
            print(f"  Extracted Source: {data.get('source')}")
            print(f"  Extracted Destination: {data.get('destination')}")
            print(f"  Matched: {data.get('matched')}")
        else:
            print(f"Failed to parse '{text}': {data.get('error')}")
    except Exception as e:
        print(f"Error connecting to voice server: {e}")

if __name__ == "__main__":
    print("Testing Semantic Voice Intent Extraction...")
    print("-" * 40)
    test_voice_parse("Take me from the main entrance to the seminar hall")
    test_voice_parse("I'm at the stairs, go to table")
    test_voice_parse("go to cabin 1 from office")
    test_voice_parse("navigate to washroom")
    test_voice_parse("i want to go from the window to the girls toilet")
