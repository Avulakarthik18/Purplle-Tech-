import cv2
import os
import json
import time
import requests
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from events import EventEngine

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:9000") + "/events/ingest"
VIDEO_DIR = "data/dataset/videos"
TRACKING_FILE = "data/tracking_output.json"
EVENTS_FILE = "data/events.json"

# Load YOLO model
model = YOLO("yolov8n.pt")

def emit_to_api(events):
    """Helper to stream events to the Intelligence API in real-time."""
    if not events:
        return
    try:
        batch = events if isinstance(events, list) else [events]
        requests.post(API_URL, json=batch, timeout=2)
    except Exception as e:
        # We don't want to crash the pipeline if the API is momentarily down
        pass

def process_video(video_path, event_engine):
    print(f"\n[ENGINE] Processing: {video_path}")
    video_name = os.path.basename(video_path)
    
    # Extract Store/Camera IDs
    parent_dir = os.path.basename(os.path.dirname(video_path))
    store_id = parent_dir if parent_dir.startswith("STORE") else "STORE_BLR_002"
    camera_id = video_name.split(".")[0]

    tracker = DeepSort(max_age=30)
    cap = cv2.VideoCapture(video_path)
    
    video_tracking_data = []
    video_events = []

    last_timestamp = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        timestamp = time.time()
        last_timestamp = timestamp

        results = model(frame, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0: # Person
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append(([x1, y1, x2-x1, y2-y1], float(box.conf[0]), "person"))

        tracks = tracker.update_tracks(detections, frame=frame)
        for track in tracks:
            if not track.is_confirmed(): continue
            
            l, t, w, h = map(int, track.to_ltrb())
            
            # Generate behavioral events
            events = event_engine.generate_event(track.track_id, [l, t, w, h], timestamp, store_id, camera_id)
            if events:
                video_events.extend(events if isinstance(events, list) else [events])
                emit_to_api(events) # <--- REAL-TIME STREAMING TO API

    # Finalize (Exit events)
    exit_events = event_engine.finalize_sessions(last_timestamp + 6)
    video_events.extend(exit_events)
    emit_to_api(exit_events)

    cap.release()
    return video_tracking_data, video_events

def run_engine():
    event_engine = EventEngine()
    if not os.path.exists("data"): os.makedirs("data")

    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            if file.endswith(".mp4"):
                process_video(os.path.join(root, file), event_engine)

    print(f"\n[DONE] Store Intelligence Engine is idle.")

if __name__ == "__main__":
    run_engine()
