import cv2
import os
import json
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

print("Loading model...")
model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

video_path = "data/dataset/videos/CAM 1.mp4"
cap = cv2.VideoCapture(video_path)

print(f"Processing 10 frames of {video_path}...")
for i in range(10):
    ret, frame = cap.read()
    if not ret: break
    
    frame = cv2.resize(frame, (640, 480))
    results = model(frame, verbose=False)
    
    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            if int(box.cls[0]) == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(([x1, y1, x2-x1, y2-y1], float(box.conf[0]), "person"))
    
    tracks = tracker.update_tracks(detections, frame=frame)
    print(f"Frame {i}: Detected {len(detections)} people, Tracking {len([t for t in tracks if t.is_confirmed()])} confirmed objects")

cap.release()
print("Test complete.")
