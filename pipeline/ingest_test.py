import json
import requests

EVENTS_FILE = "data/events.json"
API_URL = "http://127.0.0.1:8000/events/ingest"

def ingest():
    try:
        with open(EVENTS_FILE, "r") as f:
            events = json.load(f)
        
        print(f"Ingesting {len(events)} events...")
        response = requests.post(API_URL, json=events)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    except Exception as e:
        print(f"Failed to ingest: {e}")

if __name__ == "__main__":
    ingest()
