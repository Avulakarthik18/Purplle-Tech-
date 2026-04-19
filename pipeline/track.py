import cv2
import os
import json
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from events import EventEngine

# Load YOLO model
model = YOLO("yolov8n.pt")

VIDEO_DIR = "data/dataset/videos"
TRACKING_FILE = "data/tracking_output.json"
EVENTS_FILE = "data/events.json"

def process_video(video_path, event_engine):
    print(f"\n[PIPELINE] Processing: {video_path}")
    video_name = os.path.basename(video_path)
    
    # Reset tracker for each video to avoid ID collisions if cameras are independent
    tracker = DeepSort(max_age=30)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open video: {video_path}")
        return [], []

    video_tracking_data = []
    video_events = []

    last_timestamp = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize for performance
        frame = cv2.resize(frame, (640, 480))
        timestamp = time.time()
        last_timestamp = timestamp

        # Run YOLO detection
        results = model(frame, verbose=False)

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                # Class 0 = person
                if cls == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    w = x2 - x1
                    h = y2 - y1
                    detections.append(([x1, y1, w, h], conf, "person"))

        # Update tracker
        tracks = tracker.update_tracks(detections, frame=frame)

        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            l, t, w, h = map(int, track.to_ltrb())

            # 1. Store tracking result
            video_tracking_data.append({
                "video": video_name,
                "timestamp": timestamp,
                "track_id": track_id,
                "bbox": [l, t, w, h]
            })

            # 2. Generate Events
            events = event_engine.generate_event(track_id, [l, t, w, h], timestamp)
            if events:
                if isinstance(events, list):
                    video_events.extend(events)
                else:
                    video_events.append(events)

        # Handle headless display if needed
        try:
            if cv2.waitKey(1) & 0xFF == 27:
                break
        except Exception:
            pass

        # Limit detections per video for speed (set to high value for production)
        if len(video_tracking_data) > 500: 
             break

    # 3. Finalize Sessions (Exit Logic)
    exit_events = event_engine.finalize_sessions(last_timestamp + 6) # Force exit check
    video_events.extend(exit_events)

    cap.release()
    return video_tracking_data, video_events

def run_all_videos():
    all_tracking_data = []
    all_events = []
    
    event_engine = EventEngine()
    
    if not os.path.exists("data"):
        os.makedirs("data")

    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            if file.endswith(".mp4"):
                video_path = os.path.join(root, file)
                t_data, e_data = process_video(video_path, event_engine)
                all_tracking_data.extend(t_data)
                all_events.extend(e_data)

    # Save Results
    with open(TRACKING_FILE, "w") as f:
        json.dump(all_tracking_data, f, indent=4)
    
    with open(EVENTS_FILE, "w") as f:
        json.dump(all_events, f, indent=2)
    
    print(f"\n[DONE] Processing complete.")
    print(f"  - Tracking data: {len(all_tracking_data)} points saved to {TRACKING_FILE}")
    print(f"  - Events: {len(all_events)} generated and saved to {EVENTS_FILE}")
    
    try:
        cv2.destroyAllWindows()
    except:
        pass

if __name__ == "__main__":
    run_all_videos()
