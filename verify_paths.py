import requests
import json

def test_path(source, destination):
    url = "http://localhost:5050/api/find-path"
    payload = {
        "source": source,
        "destination": destination
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        if response.status_code == 200:
            print(f"Path from {source} to {destination}: Found!")
            path = [n['key'].split('::')[1] for n in data['path_nodes']]
            print(f"  Nodes: {' -> '.join(path)}")
            print(f"  Total Distance: {data['total_distance_m']}m")
            print(f"  Total Steps: {data['total_steps']}")
        else:
            print(f"Path from {source} to {destination}: Failed! {data.get('error')}")
    except Exception as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    # Test cases from 1 to various points
    test_path("1", "19")
    test_path("1", "21")
    test_path("5", "22")
    test_path("14", "15")
