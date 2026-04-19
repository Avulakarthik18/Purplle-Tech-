from ultralytics import YOLO
import cv2
import os

# Load model once
model = YOLO("yolov8n.pt")

VIDEO_DIR = "data/dataset/videos"

def run_detection():
    print(f"\n[SCANNING] Looking for videos in {VIDEO_DIR}...")
    video_found = False
    
    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            if file.endswith(".mp4"):
                video_found = True
                video_path = os.path.join(root, file)
                print(f"\n[DETECTION] Processing: {video_path}")

                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print(f"[ERROR] Could not open {video_path}")
                    continue

                frame_count = 0
                while frame_count < 5: # Limit to 5 frames for validation
                    ret, frame = cap.read()
                    if not ret:
                        break

                    results = model(frame, verbose=False)
                    
                    # Print detection summary for the frame
                    labels = results[0].boxes.cls.cpu().tolist()
                    names = results[0].names
                    detections = [names[int(l)] for l in labels]
                    
                    print(f"  - Frame {frame_count}: Detected {detections if detections else 'nothing'}")
                    
                    # Try to show, but handle headless environments
                    try:
                        annotated = results[0].plot()
                        cv2.imshow("Detection", annotated)
                        if cv2.waitKey(1) & 0xFF == 27:
                            break
                    except Exception:
                        pass # Silently skip imshow if it fails
                    
                    frame_count += 1

                cap.release()
    
    if not video_found:
        print("[ERROR] No .mp4 videos found in the dataset directory.")
    
    try:
        cv2.destroyAllWindows()
    except:
        pass

if __name__ == "__main__":
    run_detection()
