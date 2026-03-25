import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.services.s3 import upload_local_file_to_s3

VIDEO_FILES = [
    (os.path.join(BASE_DIR, "frontend/videos/step1.mp4"), "videos/step1.mp4"),
    (os.path.join(BASE_DIR, "frontend/videos/step2.mp4"), "videos/step2.mp4"),
    (os.path.join(BASE_DIR, "frontend/videos/step3.mp4"), "videos/step3.mp4"),
    (os.path.join(BASE_DIR, "frontend/videos/step4.mp4"), "videos/step4.mp4"),
    (os.path.join(BASE_DIR, "frontend/videos/step5.mp4"), "videos/step5.mp4"),
]

if __name__ == "__main__":
    for local_path, s3_key in VIDEO_FILES:
        try:
            url = upload_local_file_to_s3(local_path, s3_key, "video/mp4")
            print(f"上傳成功: {url}")
        except Exception as e:
            print(f"上傳失敗: {local_path}")
            print(e)