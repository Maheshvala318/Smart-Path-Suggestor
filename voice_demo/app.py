import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def load_valid_locations():
    """Load valid labels from the ground floor JSON."""
    path = os.path.join(os.path.dirname(__file__), "..", "department_pathfinder", "data", "ground_floor.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return [info["label"] for info in data["nodes"].values()]
    except Exception as e:
        print(f"Error loading locations: {e}")
        return []

valid_locations = load_valid_locations()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_intent():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({
            "source": "",
            "destination": "",
            "raw_text": text,
            "error": "GEMINI_API_KEY not found in .env. Please add it to use the LLM."
        }), 200 # Returning 200 with soft error so frontend can natively fallback if needed

    try:
        # LLM Integration for intent parsing using Google Gemini API
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Find an available model automatically to avoid 404 errors
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        available_model = 'gemini-1.5-flash' # fallback default
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name or 'pro' in m.name:
                        available_model = m.name.replace('models/', '')
                        break
        except Exception as e:
            print(f"Warning: Could not list models ({e}). Using default: {available_model}")

        print(f"Executing intent parsing using model: {available_model}")
        model = genai.GenerativeModel(available_model)

        prompt = f"""
        Extract the navigation source and destination from the user's request.

        USER REQUEST: "{text}"

        VALID LOCATIONS:
        {", ".join(valid_locations)}

        INSTRUCTIONS:
        1. Match the mentioned 'source' and 'destination' to the closest item in the VALID LOCATIONS list above based on keyword or semantic meaning.
        2. If a location is not found in the list, try to guess the most likely intended location from the list.
        3. If it's completely ambiguous or not even slightly matching, use an empty string.
        4. Return ONLY a valid JSON object with 'source' and 'destination' keys.

        EXAMPLE: {{"source": "1: Main Door", "destination": "15: Seminar Hall"}}
        """
        response = model.generate_content(prompt)
        content = response.text.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(content)

        return jsonify({
            "source": result_json.get("source", ""),
            "destination": result_json.get("destination", ""),
            "raw_text": text,
            "matched": True if result_json.get("source") or result_json.get("destination") else False
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=========================================")
    print("🤖 Voice Agent Intent Parser API Started")
    print("=========================================")
    print("If you haven't already, add your GEMINI_API_KEY to the .env file")
    print("Local URL: http://localhost:5001")
    app.run(debug=True, port=5001)
