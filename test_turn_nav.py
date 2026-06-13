import requests
import json

r = requests.post('http://localhost:5050/api/find-path', json={
    'source_key': 'CAMPUS::1',
    'destination_key': 'CAMPUS::13',
    'source': 'ATAL KALAM',
    'destination': 'DEPARTMENT OF COMPUTER SCIENCE'
})

d = r.json()
print("=" * 70)
print("VOICE SCRIPT:")
print("=" * 70)
print(d.get('voice_script', 'N/A'))
print()
print("=" * 70)
print("SEGMENTS:")
print("=" * 70)
for s in d.get('segments', []):
    print(f"  Step {s['step']}: {s['direction']} | {s['distance_m']}m | {s.get('note','')}")
