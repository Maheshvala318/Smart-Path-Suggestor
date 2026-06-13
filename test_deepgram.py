import requests

DEEPGRAM_API_KEY = "524cf38617d9085eebecea2efcce49098edd336c"

# Deepgram Aura models: 
# aura-asteria-en (female), aura-orion-en (male), aura-athena-en (UK female)
# (Deepgram's TTS is mostly US/UK focused currently, but let's test the UK voice as it sounds distinct)

url = "https://api.deepgram.com/v1/speak?model=aura-athena-en"
headers = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "application/json"
}

text = "Starting navigation. Start walking straight for about 80 meters. Turn left and continue for 120 meters. You will pass the Department of Botany on your left. You have arrived at the Department of Computer Science."

payload = {
    "text": text
}

print("Sending request to Deepgram TTS...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    output_file = "test_deepgram_voice.mp3"
    with open(output_file, "wb") as f:
        f.write(response.content)
    print(f"Success! Audio saved to {output_file}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
