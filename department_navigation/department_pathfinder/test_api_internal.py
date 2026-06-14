import requests
import json

def test_api():
    url = "http://localhost:5050/api/find-path"
    payload = {
        "source": "CANTEEN",
        "destination": "SCHOOL OF DESIGN",
        "source_key": "CANTEEN",
        "destination_key": "SCHOOL OF DESIGN"
    }
    try:
        r = requests.post(url, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Response: {r.text}")
            return
            
        data = r.json()
        print(f"Success: {data.get('success')}")
        print(f"Path Length: {len(data.get('path_nodes', []))}")
        if data.get('path_nodes'):
            print("Nodes summary:")
            all_have_coords = True
            for node in data['path_nodes']:
                label = node.get('label')
                lat = node.get('lat')
                lon = node.get('lon')
                if lat is None or lon is None:
                    print(f" !!! MISSING COORDS: {label}")
                    all_have_coords = False
                else:
                    # Print first and last
                    if node == data['path_nodes'][0] or node == data['path_nodes'][-1]:
                        print(f" - {label}: ({lat}, {lon})")
            if all_have_coords:
                print("PASSED: All nodes have coordinates.")
            else:
                print("FAILED: Some nodes are missing coordinates.")
        else:
            print("No path nodes found!")
        print(f"Mode: {data.get('mode')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
