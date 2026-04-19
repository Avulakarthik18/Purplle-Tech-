import cv2
import os

VIDEO_DIR = "data/dataset/videos"

def test_videos():
    for root, dirs, files in os.walk(VIDEO_DIR):
        for file in files:
            if file.endswith(".mp4"):
                video_path = os.path.join(root, file)
                print(f"\n[VIDEO] Testing: {video_path}")

                cap = cv2.VideoCapture(video_path)

                if not cap.isOpened():
                    print("[ERROR] Cannot open video")
                    continue

                ret, frame = cap.read()
                if ret:
                    print("[OK] Frame read successfully")
                    print("Frame shape:", frame.shape)
                else:
                    print("[ERROR] Failed to read frame")

                cap.release()

if __name__ == "__main__":
    test_videos()
