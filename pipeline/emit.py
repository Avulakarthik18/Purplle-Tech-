import json
import requests
import time

EVENTS_FILE = "data/events.json"
API_URL = "http://localhost:9000/events/ingest"

def emit_events():
    try:
        with open(EVENTS_FILE, "r") as f:
            events = json.load(f)
        
        print(f"[EMITTER] Found {len(events)} events. Sending to API...")
        
        # Send in batches of 100
        batch_size = 100
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            response = requests.post(API_URL, json=batch)
            if response.status_code == 200:
                print(f"  - Batch {i//batch_size + 1} sent successfully.")
            else:
                print(f"  - Error sending batch {i//batch_size + 1}: {response.text}")
            
    except FileNotFoundError:
        print(f"[ERROR] Events file not found at {EVENTS_FILE}. Run track.py first.")
    except Exception as e:
        print(f"[ERROR] Emitter failed: {e}")

if __name__ == "__main__":
    emit_events()
